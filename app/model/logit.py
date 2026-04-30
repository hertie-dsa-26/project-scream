import csv
import math
import random
import os
import urllib.request
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/hertie-dsa-26/project-scream/refs/heads/main/literature/diabetes_risk_literature_subset.csv"
DATA_FILE = "diabetes_risk_literature_subset.csv"
RANDOM_SEED = 42

# ─────────────────────────────────────────────────────────────────────────────
# 1. SCRATCH IMPLEMENTATION BITS
# ─────────────────────────────────────────────────────────────────────────────
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def train_scratch(X, y, lr=0.1, epochs=500):
    n, p = X.shape
    w, b = np.zeros(p), 0.0
    for _ in range(epochs):
        z = np.dot(X, w) + b
        probs = sigmoid(z)
        err = probs - y
        dw = np.dot(X.T, err) / n
        db = np.sum(err) / n
        w -= lr * dw
        b -= lr * db
    return w, b

# ─────────────────────────────────────────────────────────────────────────────
# 2. DATA PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline():
    print("\n[STEP 1] Loading and Cleaning Data...")
    if not os.path.exists(DATA_FILE):
        urllib.request.urlretrieve(DATA_URL, DATA_FILE)

    with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = [h.strip().upper() for h in next(reader)]
        rows = list(reader)

    col_idx = {h: i for i, h in enumerate(header)}
    target = "HAS_DIABETES"
    features = [h for h in header if h != target]

    X_raw, y_raw = [], []
    for row in rows:
        try:
            # FIX: Map 1.0 -> 1 (Yes), 2.0 -> 0 (No)
            lbl = float(row[col_idx[target]])
            if lbl == 1.0: y_raw.append(1)
            elif lbl == 2.0: y_raw.append(0)
            else: continue

            X_raw.append([float(row[col_idx[f]]) if row[col_idx[f]] else None for f in features])
        except: continue

    # Convert to Numpy for easier math
    X_np = np.array(X_raw, dtype=float)
    y_np = np.array(y_raw)

    # Median Imputation
    col_medians = np.nanmedian(X_np, axis=0)
    inds = np.where(np.isnan(X_np))
    X_np[inds] = np.take(col_medians, inds[1])

    print(f"  > Valid cases: {len(y_np)} (Diabetes: {sum(y_np)}, Healthy: {len(y_np)-sum(y_np)})")
    return X_np, y_np, features, col_medians

# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPARISON EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    X, y, feat_names, medians = run_pipeline()

    # Shuffle and Split
    np.random.seed(RANDOM_SEED)
    indices = np.arange(len(y))
    np.random.shuffle(indices)
    split = int(len(y) * 0.8)

    X_train, X_test = X[indices[:split]], X[indices[split:]]
    y_train, y_test = y[indices[:split]], y[indices[split:]]

    # Standardization
    means = np.mean(X_train, axis=0)
    stds = np.std(X_train, axis=0)
    stds[stds == 0] = 1.0
    X_train_std = (X_train - means) / stds
    X_test_std = (X_test - means) / stds

    # --- MODEL 1: FROM SCRATCH ---
    print("\n[STEP 2] Training Custom Model (Scratch)...")
    w_s, b_s = train_scratch(X_train_std, y_train.astype(float))
    scratch_probs = sigmoid(np.dot(X_test_std, w_s) + b_s)
    scratch_preds = (scratch_probs >= 0.5).astype(int)
    acc_s = accuracy_score(y_test, scratch_preds)

    # --- MODEL 2: SCIKIT-LEARN ---
    print("[STEP 3] Training Scikit-Learn Model...")
    sk_model = LogisticRegression(max_iter=500, solver='lbfgs')
    sk_model.fit(X_train_std, y_train)
    sk_preds = sk_model.predict(X_test_std)
    sk_probs = sk_model.predict_proba(X_test_std)[:, 1]
    acc_sk = accuracy_score(y_test, sk_preds)

    print(f"\n{'═'*40}\n  COMPARISON RESULTS\n{'═'*40}")
    print(f"Scratch Accuracy:    {acc_s*100:.2f}%")
    print(f"Scikit-Learn Acc:   {acc_sk*100:.2f}%")

    # ─────────────────────────────────────────────────────────────────────────────
    # 4. FINAL EXAMPLES
    # ─────────────────────────────────────────────────────────────────────────────
    profile_a = {"AGE_IMPUTED": 22, "GENERAL_HEALTH": 1, "BMI": 19.0, "HIGH_BP": 0, "EXERCISE": 1}
    profile_b = {"AGE_IMPUTED": 75, "GENERAL_HEALTH": 5, "BMI": 38.0, "HIGH_BP": 1, "EXERCISE": 0}

    print(f"\n{'═'*40}\n  PREDICTION COMPARISON\n{'═'*40}")
    for name, prof in [("Healthy User", profile_a), ("High Risk User", profile_b)]:
        # Prepare sample
        sample = np.array([prof.get(f, medians[i]) for i, f in enumerate(feat_names)])
        sample_std = (sample - means) / stds

        # Predict both
        p_scratch = sigmoid(np.dot(sample_std, w_s) + b_s)
        p_sk = sk_model.predict_proba(sample_std.reshape(1, -1))[0][1]

        print(f"\n{name}:")
        print(f"  Features: {prof}")
        print(f"  [Scratch] Risk: {p_scratch*100:.1f}%")
        print(f"  [Sklearn] Risk: {p_sk*100:.1f}%")

if __name__ == "__main__":
    main()