"""
Model interface for the diabetes risk predictor.

Public API
----------
load_model()   -> None          call once at app startup (in create_app)
predict(inputs) -> PredictResult  call per request from routes

The rest of this module is private.
"""

from __future__ import annotations

import json
import joblib
from pathlib import Path
from dataclasses import dataclass

import pandas as pd

# ---------------------------------------------------------------------------
# Paths & cache
# ---------------------------------------------------------------------------

_ARTIFACTS = Path(__file__).parent.parent / "model" / "artifacts"

_cache: dict = {}

# ---------------------------------------------------------------------------
# Risk categorisation thresholds (probability, not percentage)
# ---------------------------------------------------------------------------

_THRESHOLDS = {
    "low":      (0.00, 0.10),
    "moderate": (0.10, 0.25),
    "high":     (0.25, 1.01),
}

# ---------------------------------------------------------------------------
# Actionable features — modifications we counterfactually test
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
        "always_show": True,  # show regardless of model delta — evidence is clear
    },
]

# Tip that is always shown (not model-derived)
_DIET_TIP = {
    "label": "Improve your diet",
    "tip": (
        "Reducing sugar, processed foods, and refined carbs is one of the "
        "strongest evidence-based ways to prevent diabetes — an effect our "
        "model does not directly capture."
    ),
    "static": True,
}

# ---------------------------------------------------------------------------
# Median fill-ins for features not collected from the user
# ---------------------------------------------------------------------------

_MEDIAN_KEYS = ["height_inches", "weight_kg"]


# ---------------------------------------------------------------------------
# Public dataclass for prediction results
# ---------------------------------------------------------------------------

@dataclass
class PredictResult:
    probability: float          # 0–1
    probability_pct: float      # 0–100, rounded to 1 dp
    risk_category: str          # "low" | "moderate" | "high"
    suggestions: list[dict]     # actionable tips with counterfactual deltas
    input_features: dict        # the full feature dict passed to the model


# ---------------------------------------------------------------------------
# Private loaders
# ---------------------------------------------------------------------------

def _load_pipeline():
    path = _ARTIFACTS / "pipeline.joblib"
    if not path.exists():
        raise RuntimeError(
            f"Model artifact not found at {path}. "
            "Run: uv run python train_model.py"
        )
    return joblib.load(path)


def _load_metrics() -> dict:
    path = _ARTIFACTS / "metrics.json"
    if not path.exists():
        raise RuntimeError(f"Metrics file not found at {path}.")
    with open(path) as f:
        return json.load(f)


def _load_coefficients() -> list[dict]:
    path = _ARTIFACTS / "coefficients.json"
    if not path.exists():
        raise RuntimeError(f"Coefficients file not found at {path}.")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model() -> None:
    """
    Eagerly load all model artifacts into the module-level cache.
    Call this once inside create_app() so the first prediction request
    is not penalised by cold-load latency.
    """
    _cache["pipeline"]     = _load_pipeline()
    _cache["metrics"]      = _load_metrics()
    _cache["coefficients"] = _load_coefficients()


def get_pipeline():
    if "pipeline" not in _cache:
        _cache["pipeline"] = _load_pipeline()
    return _cache["pipeline"]


def get_metrics() -> dict:
    if "metrics" not in _cache:
        _cache["metrics"] = _load_metrics()
    return _cache["metrics"]


def get_coefficients() -> list[dict]:
    if "coefficients" not in _cache:
        _cache["coefficients"] = _load_coefficients()
    return _cache["coefficients"]


def predict(validated_inputs: dict) -> PredictResult:
    """
    Run the model on validated, cleaned inputs from validation.py.

    Parameters
    ----------
    validated_inputs : dict
        Output of validate_prediction_input() — contains age_imputed,
        bmi_x100, and all categorical features as floats.

    Returns
    -------
    PredictResult
    """
    pipeline = get_pipeline()
    medians  = get_metrics()["numeric_medians"]

    # Fill in features not collected from the user
    full_inputs = {**validated_inputs}
    for key in _MEDIAN_KEYS:
        full_inputs.setdefault(key, medians[key])

    # Base prediction
    df       = pd.DataFrame([full_inputs])
    base_prob = float(pipeline.predict_proba(df)[0, 1])

    # Risk category
    risk_category = "high"  # fallback
    for category, (lo, hi) in _THRESHOLDS.items():
        if lo <= base_prob < hi:
            risk_category = category
            break

    # Counterfactual suggestions
    suggestions: list[dict] = []
    for action in _ACTIONABLE:
        val = full_inputs.get(action["key"])
        if val is not None and action["active_if"](val):
            modified  = {**full_inputs, action["key"]: action["best"]}
            new_prob  = float(pipeline.predict_proba(pd.DataFrame([modified]))[0, 1])
            delta_pct = (base_prob - new_prob) * 100
            if delta_pct > 0.5 or action.get("always_show"):
                suggestions.append({
                    "label":        action["label"],
                    "tip":          action["tip"],
                    "new_prob_pct": round(new_prob * 100, 1),
                    "delta_pct":    round(delta_pct, 1),
                    "static":       False,
                })

    suggestions.append(_DIET_TIP)

    return PredictResult(
        probability      = base_prob,
        probability_pct  = round(base_prob * 100, 1),
        risk_category    = risk_category,
        suggestions      = suggestions,
        input_features   = full_inputs,
    )