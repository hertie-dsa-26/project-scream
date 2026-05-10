"""
retrain_svm.py
==============
Retrains the ManualSVM and saves fresh artifacts compatible with the
current sklearn version. ManualSVM is imported from app.utils.model so
joblib serialises it as app.utils.model.ManualSVM — not __main__.ManualSVM —
making it loadable by the Flask app.

Run from the project root:
    uv run python retrain_svm.py

Output files (written to app/model/artifacts/):
    svm_model.pkl
    scaler.pkl
    feature_columns.json
"""

import json
import sys
from pathlib import Path

# Must come before other app imports so the path is set
sys.path.insert(0, str(Path(__file__).parent))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, recall_score, precision_score,
    f1_score, roc_auc_score, confusion_matrix,
)

# Import ManualSVM from the app so pickle stores the correct module path
from app.utils.model import ManualSVM

# ── Paths ──────────────────────────────────────────────────────────────────────

DATA_PATH = Path("literature/diabetes_risk_literature_subset.csv")
OUT_DIR   = Path("app/model/artifacts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Features ───────────────────────────────────────────────────────────────────

FEATURES = [
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

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    X = df[FEATURES]
    y = df["has_diabetes_binary"]

    print(f"Dataset: {X.shape[0]:,} rows, {X.shape[1]} features")
    print(f"Positive rate: {y.mean():.3f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nFitting scaler...")
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    print("Training ManualSVM (n_iters=300, this may take a few minutes)...")
    model = ManualSVM(
        lr=0.001,
        lambda_param=0.01,
        n_iters=300,
        class_weight={-1: 1.0, 1: 5.0},
    )
    model.fit(X_train_s, y_train.values)

    print("\nEvaluating...")
    preds  = model.predict(X_test_s)
    scores = model.decision_score(X_test_s)

    print(f"Accuracy  : {accuracy_score(y_test, preds):.4f}")
    print(f"Recall    : {recall_score(y_test, preds):.4f}")
    print(f"Precision : {precision_score(y_test, preds):.4f}")
    print(f"F1        : {f1_score(y_test, preds):.4f}")
    print(f"ROC-AUC   : {roc_auc_score(y_test, scores):.4f}")
    print(f"Confusion matrix:\n{confusion_matrix(y_test, preds)}")

    print(f"\nSaving artifacts to {OUT_DIR}/...")
    joblib.dump(model,  OUT_DIR / "svm_model.pkl")
    joblib.dump(scaler, OUT_DIR / "scaler.pkl")
    with open(OUT_DIR / "feature_columns.json", "w") as f:
        json.dump(FEATURES, f)

    print("Done.")
    print("  svm_model.pkl")
    print("  scaler.pkl")
    print("  feature_columns.json")


if __name__ == "__main__":
    main()