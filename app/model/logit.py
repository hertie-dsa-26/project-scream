"""Logistic regression model for diabetes prediction (BRFSS 2024).

Input:  literature/diabetes_risk_literature_subset_final.csv
Target: has_diabetes_binary  (1 = diabetic/pre-diabetic, 0 = no)
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

_BASE = Path(__file__).parent.parent.parent
DATA_PATH = _BASE / "literature" / "diabetes_risk_literature_subset.csv"
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"

TARGET = "has_diabetes_binary"

NUMERIC_FEATURES = [
    "age_imputed",
    "bmi_x100",
    "height_inches",
    "weight_kg",
]

CATEGORICAL_FEATURES = [
    "sex",
    "general_health",
    "education_level",
    "income_level",
    "smoking_status",
    "any_physical_activity",
    "any_alcohol_past_30d",
]


def load_data(path: Path = DATA_PATH) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    missing = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in data: {missing}")

    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X = df[features].copy()
    y = df[TARGET].astype(int)
    return X, y


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(drop="first", sparse_output=False), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def fit_sklearn(X_train, y_train, X_test, y_test) -> None:
    pipe = Pipeline([
        ("prep", build_preprocessor()),
        ("clf", LogisticRegression(max_iter=1000, solver="lbfgs", random_state=42)),
    ])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    print("─── sklearn LogisticRegression ───")
    print(classification_report(y_test, y_pred, target_names=["No Diabetes", "Diabetes"]))
    print(f"ROC-AUC : {roc_auc_score(y_test, y_prob):.4f}")
    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))
    print()

    return pipe


def fit_statsmodels(X_train, y_train, X_test, y_test) -> None:
    """Fit via statsmodels for coefficient-level inference (odds ratios, p-values)."""
    prep = build_preprocessor()
    X_train_t = prep.fit_transform(X_train, y_train)
    X_test_t = prep.transform(X_test)

    # Recover feature names for readable output
    cat_enc: OneHotEncoder = prep.named_transformers_["cat"]
    cat_names = cat_enc.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names = NUMERIC_FEATURES + cat_names

    X_train_sm = sm.add_constant(X_train_t)
    X_test_sm = sm.add_constant(X_test_t)

    model = sm.Logit(y_train.values, X_train_sm)
    result = model.fit(method="lbfgs", maxiter=1000, disp=False)

    print("─── statsmodels Logit summary ───")
    print(result.summary2(xname=["const"] + feature_names))

    # Odds ratios
    odds = pd.DataFrame({
        "OR": np.exp(result.params[1:]),
        "p-value": result.pvalues[1:],
    }, index=feature_names).sort_values("OR", ascending=False)
    print("\nOdds Ratios (sorted):")
    print(odds.to_string(float_format="{:.4f}".format))

    return result


def train_and_save(
    data_path: Path = DATA_PATH,
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> dict:
    """Train the model and save pipeline + metrics. Run once before starting Flask."""
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    X, y = load_data(data_path)
    numeric_medians = {col: float(X[col].median()) for col in NUMERIC_FEATURES}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("prep", build_preprocessor()),
        ("clf", LogisticRegression(max_iter=1000, solver="lbfgs", random_state=42)),
    ])
    pipe.fit(X_train, y_train)
    joblib.dump(pipe, artifacts_dir / "pipeline.joblib")

    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_prob)
    report = classification_report(
        y_test, y_pred,
        target_names=["No Diabetes", "Diabetes"],
        output_dict=True,
    )

    prep_sm = build_preprocessor()
    X_train_t = prep_sm.fit_transform(X_train, y_train)
    cat_enc: OneHotEncoder = prep_sm.named_transformers_["cat"]
    cat_names = cat_enc.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names = NUMERIC_FEATURES + cat_names

    sm_result = sm.Logit(y_train.values, sm.add_constant(X_train_t)).fit(
        method="lbfgs", maxiter=1000, disp=False
    )

    coefficients = sorted(
        [
            {
                "feature": name,
                "coef": float(c),
                "odds_ratio": float(np.exp(c)),
                "p_value": float(p),
            }
            for name, c, p in zip(feature_names, sm_result.params[1:], sm_result.pvalues[1:])
        ],
        key=lambda x: x["odds_ratio"],
        reverse=True,
    )

    metrics = {
        "roc_auc": round(roc_auc, 4),
        "accuracy": round(report["accuracy"], 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "positive_rate": round(float(y.mean()), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "numeric_medians": numeric_medians,
    }

    (artifacts_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (artifacts_dir / "coefficients.json").write_text(json.dumps(coefficients, indent=2))
    print(f"ROC-AUC: {roc_auc:.4f}  |  artifacts → {artifacts_dir}")
    return metrics


def load_pipeline(artifacts_dir: Path = ARTIFACTS_DIR) -> Pipeline:
    return joblib.load(artifacts_dir / "pipeline.joblib")


def main() -> None:
    print(f"Loading data from {DATA_PATH}...")
    X, y = load_data()
    print(f"  Shape: {X.shape},  Positive rate: {y.mean():.3f}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    sklearn_model = fit_sklearn(X_train, y_train, X_test, y_test)
    sm_result = fit_statsmodels(X_train, y_train, X_test, y_test)


if __name__ == "__main__":
    main()
