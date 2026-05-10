"""
Model interface for the diabetes risk predictor.

Public API
----------
load_model()    -> None           call once at app startup (in create_app)
predict(inputs) -> PredictResult  call per request from routes
get_svm()       -> ManualSVM
get_scaler()    -> StandardScaler
get_feature_columns() -> list[str]

The rest of this module is private.
"""

from __future__ import annotations

import json
import joblib
import numpy as np
from pathlib import Path
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Paths & cache
# ---------------------------------------------------------------------------

_ARTIFACTS = Path(__file__).parent.parent / "model" / "artifacts"

_cache: dict = {}

# ---------------------------------------------------------------------------
# ManualSVM class definition (must match retrain_svm.py exactly so joblib
# can deserialise the saved artifact)
# ---------------------------------------------------------------------------

class ManualSVM:
    def __init__(self, lr=0.001, lambda_param=0.01, n_iters=100, class_weight=None):
        self.lr            = lr
        self.lambda_param  = lambda_param
        self.n_iters       = n_iters
        self.class_weight  = class_weight
        self.w             = None
        self.b             = None

    def _compute_class_weights(self, y_internal):
        classes   = np.unique(y_internal)
        n_samples = len(y_internal)
        return {
            c: n_samples / (len(classes) * np.sum(y_internal == c))
            for c in classes
        }

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features)
        self.b = 0
        y_ = np.where(y == 0, -1, 1)
        if self.class_weight == "balanced":
            cw = self._compute_class_weights(y_)
        elif isinstance(self.class_weight, dict):
            cw = self.class_weight
        else:
            cw = {c: 1.0 for c in np.unique(y_)}
        sample_weights = np.array([cw[label] for label in y_])
        for _ in range(self.n_iters):
            for i in range(n_samples):
                condition = y_[i] * (np.dot(X[i], self.w) - self.b) >= 1
                if condition:
                    self.w -= self.lr * (2 * self.lambda_param * self.w)
                else:
                    self.w -= self.lr * (
                        2 * self.lambda_param * self.w
                        - sample_weights[i] * np.dot(X[i], y_[i])
                    )
                    self.b -= self.lr * sample_weights[i] * y_[i]

    def predict(self, X):
        linear_output = np.dot(X, self.w) - self.b
        return (linear_output >= 0).astype(int)

    def decision_score(self, X):
        """Raw margin score before thresholding. Used for risk scoring."""
        return np.dot(X, self.w) - self.b


# ---------------------------------------------------------------------------
# Risk scoring via sigmoid on decision score
#
# The ManualSVM has no predict_proba. We apply a sigmoid to the raw decision
# score to map it to [0, 1]. This is a standard approximation for linear SVMs
# and gives a monotone risk score suitable for thresholding and counterfactuals.
# It is NOT a calibrated probability — display as "estimated risk score", not %.
# ---------------------------------------------------------------------------

def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))


# ---------------------------------------------------------------------------
# Risk categorisation thresholds (applied to sigmoid score)
# ---------------------------------------------------------------------------

_THRESHOLDS = {
    "low":      (0.00, 0.40),
    "moderate": (0.40, 0.60),
    "high":     (0.60, 1.01),
}

# ---------------------------------------------------------------------------
# Actionable features
# ---------------------------------------------------------------------------

_ACTIONABLE: list[dict] = [
    {
        "key":       "any_physical_activity",
        "label":     "Get physically active",
        "tip":       (
            "People who exercise at least occasionally have a significantly "
            "lower estimated diabetes risk."
        ),
        "best":      1.0,
        "active_if": lambda v: v == 2.0,
    },
    {
        "key":         "smoking_status",
        "label":       "Quit smoking",
        "tip":         (
            "Quitting smoking improves metabolic health and reduces "
            "long-term diabetes risk."
        ),
        "best":        4.0,
        "active_if":   lambda v: v in (1.0, 2.0),
        "always_show": True,
    },
]

_DIET_TIP = {
    "label": "Improve your diet",
    "tip": (
        "Reducing sugar, processed foods, and refined carbs is one of the "
        "strongest evidence-based ways to prevent diabetes — an effect our "
        "model does not directly capture."
    ),
    "static": True,
}

_FEATURES = [
    "general_health",
    "any_physical_activity",
    "sex",
    "age_imputed",
    "bmi",
    "education_level",
    "income_level",
    "smoking_status",
    "any_alcohol_past_30d",
]


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------

@dataclass
class PredictResult:
    probability: float          # 0-1 sigmoid score
    probability_pct: float      # 0-100, rounded to 1 dp
    risk_category: str          # "low" | "moderate" | "high"
    suggestions: list[dict]
    input_features: dict


# ---------------------------------------------------------------------------
# Private loaders
# ---------------------------------------------------------------------------

def _load_svm() -> ManualSVM:
    path = _ARTIFACTS / "svm_model.pkl"
    if not path.exists():
        raise RuntimeError(
            f"SVM artifact not found at {path}. "
            "Run: uv run python retrain_svm.py"
        )
    return joblib.load(path)


def _load_scaler():
    path = _ARTIFACTS / "scaler.pkl"
    if not path.exists():
        raise RuntimeError(f"Scaler not found at {path}.")
    return joblib.load(path)


def _load_feature_columns() -> list[str]:
    path = _ARTIFACTS / "feature_columns.json"
    if not path.exists():
        raise RuntimeError(f"feature_columns.json not found at {path}.")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model() -> None:
    """Eagerly load all model artifacts. Call once in create_app()."""
    _cache["svm"]             = _load_svm()
    _cache["scaler"]          = _load_scaler()
    _cache["feature_columns"] = _load_feature_columns()


def get_svm() -> ManualSVM:
    if "svm" not in _cache:
        _cache["svm"] = _load_svm()
    return _cache["svm"]


def get_scaler():
    if "scaler" not in _cache:
        _cache["scaler"] = _load_scaler()
    return _cache["scaler"]


def get_feature_columns() -> list[str]:
    if "feature_columns" not in _cache:
        _cache["feature_columns"] = _load_feature_columns()
    return _cache["feature_columns"]


def _score(inputs: dict) -> float:
    """Scale inputs and return sigmoid(decision_score)."""
    import pandas as pd
    svm    = get_svm()
    scaler = get_scaler()
    X      = pd.DataFrame([[inputs[f] for f in _FEATURES]], columns=_FEATURES)
    X_s    = scaler.transform(X)
    return float(_sigmoid(svm.decision_score(X_s)[0]))


def predict(validated_inputs: dict) -> PredictResult:
    """
    Run the SVM on validated inputs from validation.py.

    Parameters
    ----------
    validated_inputs : dict
        Output of validate_prediction_input() — must contain all _FEATURES keys.
    """
    base_score = _score(validated_inputs)

    risk_category = "high"
    for category, (lo, hi) in _THRESHOLDS.items():
        if lo <= base_score < hi:
            risk_category = category
            break

    suggestions: list[dict] = []
    for action in _ACTIONABLE:
        val = validated_inputs.get(action["key"])
        if val is not None and action["active_if"](val):
            modified  = {**validated_inputs, action["key"]: action["best"]}
            new_score = _score(modified)
            delta_pct = (base_score - new_score) * 100
            if delta_pct > 0.5 or action.get("always_show"):
                suggestions.append({
                    "label":        action["label"],
                    "tip":          action["tip"],
                    "new_prob_pct": round(new_score * 100, 1),
                    "delta_pct":    round(delta_pct, 1),
                    "static":       False,
                })

    suggestions.append(_DIET_TIP)

    return PredictResult(
        probability      = base_score,
        probability_pct  = round(base_score * 100, 1),
        risk_category    = risk_category,
        suggestions      = suggestions,
        input_features   = validated_inputs,
    )