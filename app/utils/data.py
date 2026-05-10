"""
Centralized data loader with in-memory caching.

Public API
----------
load_brfss()        -> pd.DataFrame   raw dataset, cached after first read
get_benchmarks()    -> dict           per-feature means split by diabetes status
get_overall_stats() -> dict           per-feature means across full dataset
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from flask import current_app

_cache: dict = {}

# Features we compute benchmarks for — matches the model's input features
_BENCHMARK_FEATURES = [
    "age_imputed",
    "bmi_x100",
    "any_physical_activity",
    "smoking_status",
    "any_alcohol_past_30d",
    "general_health",
    "education_level",
    "income_level",
    "sex",
]

# Human-readable labels for display in templates
FEATURE_LABELS: dict[str, str] = {
    "age_imputed":           "Age",
    "bmi_x100":              "BMI (×100)",
    "any_physical_activity": "Any physical activity",
    "smoking_status":        "Smoking status",
    "any_alcohol_past_30d":  "Alcohol use (past 30 days)",
    "general_health":        "General health",
    "education_level":       "Education level",
    "income_level":          "Income level",
    "sex":                   "Sex",
    "height_inches":         "Height (inches)",
    "weight_kg":             "Weight (kg)",
}

# Categorical value labels for display
CATEGORICAL_LABELS: dict[str, dict[float, str]] = {
    "sex": {
        1.0: "Male", 2.0: "Female",
    },
    "general_health": {
        1.0: "Excellent", 2.0: "Very good", 3.0: "Good",
        4.0: "Fair",      5.0: "Poor",
    },
    "education_level": {
        1.0: "Never attended",  2.0: "Grades 1–8",
        3.0: "Grades 9–11",    4.0: "Grade 12 / GED",
        5.0: "Some college",   6.0: "College graduate",
    },
    "income_level": {
        1.0: "< $15k",    2.0: "$15–25k",   3.0: "$25–35k",
        4.0: "$35–50k",   5.0: "$50–100k",  6.0: "$100–150k",
        7.0: "$150–200k", 8.0: "> $200k",
    },
    "smoking_status": {
        1.0: "Daily smoker",   2.0: "Some-days smoker",
        3.0: "Former smoker",  4.0: "Never smoked",
    },
    "any_physical_activity": {
        1.0: "Yes", 2.0: "No",
    },
    "any_alcohol_past_30d": {
        1.0: "Yes", 2.0: "No",
    },
}


def load_brfss() -> pd.DataFrame:
    """Load the BRFSS subset, cached after first read."""
    if "brfss" not in _cache:
        path = current_app.config["DATA_DIR"] / "subsets" / "brfss2024_subset.parquet"
        _cache["brfss"] = pd.read_parquet(path)
    return _cache["brfss"]


def _diabetes_binary(df: pd.DataFrame) -> pd.Series:
    """
    Recode has_diabetes to binary on the fly.
    BRFSS codes: 1=Yes, 2=Yes (during pregnancy), 3=No, 4=No (prediabetes only).
    Codes 7 (don't know) and 9 (refused) become NaN and are excluded.
    Matches the recoding applied during model training.
    """
    return df["has_diabetes"].map({1.0: 1, 2.0: 1, 3.0: 0, 4.0: 0})


def get_benchmarks() -> dict:
    """
    Return per-feature benchmarks split by diabetes status, cached.

    Returns
    -------
    {
      "diabetic":     {feature: benchmark, ...},
      "non_diabetic": {feature: benchmark, ...},
    }

    benchmark is:
    - float (mean) for numeric features
    - dict for categorical features:
        {
          "mean":     float,
          "mode":     float,
          "mode_pct": float,   # 0..1
          "pct_yes":  float,   # 0..1 (only for binary yes/no with codes 1 and 2)
        }
    """
    if "benchmarks" not in _cache:
        df       = load_brfss()
        diabetes = _diabetes_binary(df)

        diabetic     = df[diabetes == 1]
        non_diabetic = df[diabetes == 0]

        def _bench_for_group(group_df: pd.DataFrame) -> dict:
            out: dict = {}
            for feature in _BENCHMARK_FEATURES:
                if feature not in group_df.columns:
                    continue
                series = group_df[feature].dropna()
                if series.empty:
                    continue

                if feature in CATEGORICAL_LABELS:
                    counts   = series.value_counts(dropna=True)
                    mode_val = float(counts.index[0])
                    mode_pct = float(counts.iloc[0] / counts.sum())
                    summary  = {
                        "mean":     round(float(series.mean()), 3),
                        "mode":     mode_val,
                        "mode_pct": round(mode_pct, 3),
                    }
                    labels = CATEGORICAL_LABELS.get(feature, {})
                    if set(labels.keys()) == {1.0, 2.0}:
                        summary["pct_yes"] = round(float((series == 1.0).mean()), 3)
                    out[feature] = summary
                else:
                    out[feature] = round(float(series.mean()), 3)
            return out

        _cache["benchmarks"] = {
            "diabetic":     _bench_for_group(diabetic),
            "non_diabetic": _bench_for_group(non_diabetic),
        }
    return _cache["benchmarks"]


def get_overall_stats() -> dict:
    """
    Return per-feature means across the full dataset, cached.

    Returns
    -------
    {feature: mean, ...}
    """
    if "overall_stats" not in _cache:
        df = load_brfss()
        _cache["overall_stats"] = {
            f: round(df[f].mean(), 3)
            for f in _BENCHMARK_FEATURES if f in df.columns
        }
    return _cache["overall_stats"]


def load_references() -> list[dict]:
    """Load citation references from app/references.json, cached."""
    if "references" not in _cache:
        path = Path(__file__).parent.parent / "references.json"
        with open(path) as f:
            _cache["references"] = json.load(f)
    return _cache["references"]