"""Prepare a model-ready diabetes subset for sharing and training.

This script is intentionally separate from pipeline/new_subset.py:
- new_subset.py builds the raw literature-based subset
- this script performs cleaning, recoding, and imputation

Outputs (by default):
- literature/diabetes_risk_literature_subset_final.csv
- literature/diabetes_risk_data_preparation.md
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


INPUT_PARQUET_DEFAULT = Path("data/subsets/diabetes_risk_literature_subset.parquet")
OUTPUT_CSV_DEFAULT = Path("literature/diabetes_risk_literature_subset_final.csv")
OUTPUT_MD_DEFAULT = Path("literature/diabetes_risk_data_preparation.md")

TARGET_RAW = "has_diabetes"
TARGET_BINARY = "has_diabetes_binary"

# Requested project decision: remove this high-missing feature.
DROP_FEATURES = ["food_insecurity"]

# BRFSS-specific special codes to recode as missing (column-specific to avoid false recodes).
SPECIAL_MISSING_CODES: dict[str, set[int]] = {
    "general_health": {7, 9},
    "has_diabetes": {7, 9},
    "any_physical_activity": {9},
    "education_level": {9},
    "income_level": {9},
    "smoking_status": {9},
    "any_alcohol_past_30d": {7, 9},
    "height_inches": {7777, 9999},
    "weight_kg": {77777, 99999},
    "bmi_x100": {9999},
}

# Binary target map for diabetes prediction (1/2 -> positive, 3/4 -> negative).
TARGET_MAP = {
    1: 1,
    2: 1,
    3: 0,
    4: 0,
}

NUMERIC_PREDICTORS = {
    "age_imputed",
    "height_inches",
    "weight_kg",
    "bmi_x100",
    "bmi",
}

CATEGORICAL_PREDICTORS = {
    "general_health",
    "any_physical_activity",
    "sex",
    "education_level",
    "income_level",
    "smoking_status",
    "any_alcohol_past_30d",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create final cleaned diabetes subset for Colab sharing.")
    parser.add_argument("--input-path", type=Path, default=INPUT_PARQUET_DEFAULT)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV_DEFAULT)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD_DEFAULT)
    return parser.parse_args()


def read_input(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError("Unsupported input file type. Use .parquet or .csv")


def recode_special_missing(df: pd.DataFrame) -> dict[str, int]:
    recode_counts: dict[str, int] = {}

    for col, codes in SPECIAL_MISSING_CODES.items():
        if col not in df.columns:
            continue

        numeric_view = pd.to_numeric(df[col], errors="coerce")
        mask = numeric_view.isin(codes)
        recode_counts[col] = int(mask.sum())
        df.loc[mask, col] = pd.NA

    return recode_counts


def build_binary_target(df: pd.DataFrame) -> tuple[int, int]:
    if TARGET_RAW not in df.columns:
        raise KeyError(f"Expected target column missing: {TARGET_RAW}")

    target_numeric = pd.to_numeric(df[TARGET_RAW], errors="coerce")
    df[TARGET_BINARY] = target_numeric.map(TARGET_MAP)

    rows_before = len(df)
    df.dropna(subset=[TARGET_BINARY], inplace=True)
    rows_after = len(df)
    return rows_before, rows_after


def impute_predictors(df: pd.DataFrame) -> dict[str, str]:
    fill_values: dict[str, str] = {}

    predictors = [c for c in df.columns if c not in {TARGET_RAW, TARGET_BINARY}]
    numeric_predictors = [c for c in predictors if c in NUMERIC_PREDICTORS]
    categorical_predictors = [c for c in predictors if c in CATEGORICAL_PREDICTORS]

    # Fallback: if any predictor was not explicitly listed, treat it as categorical.
    unlisted_predictors = [
        c for c in predictors if c not in set(numeric_predictors).union(categorical_predictors)
    ]
    categorical_predictors.extend(unlisted_predictors)

    for col in numeric_predictors:
        if df[col].isna().sum() == 0:
            continue
        median_val = pd.to_numeric(df[col], errors="coerce").median()
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(median_val)
        fill_values[col] = f"median={median_val}"

    for col in categorical_predictors:
        if df[col].isna().sum() == 0:
            continue
        mode_vals = df[col].mode(dropna=True)
        mode_val = mode_vals.iloc[0] if not mode_vals.empty else "Unknown"
        df[col] = df[col].fillna(mode_val)
        fill_values[col] = f"mode={mode_val}"

    return fill_values


def pct(count: int, total: int) -> str:
    if total == 0:
        return "0.00%"
    return f"{(count / total) * 100:.2f}%"


def write_markdown_report(
    md_path: Path,
    *,
    input_path: Path,
    output_csv: Path,
    rows_initial: int,
    cols_initial: int,
    dropped_features: list[str],
    recode_counts: dict[str, int],
    rows_before_target_filter: int,
    rows_after_target_filter: int,
    missing_before_impute: pd.Series,
    missing_after_impute: pd.Series,
    fill_values: dict[str, str],
) -> None:
    lines: list[str] = []

    lines.append("# Diabetes Risk Data Preparation Notes")
    lines.append("")
    lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Why this document exists")
    lines.append("")
    lines.append("This note documents how the final training CSV was prepared from the literature-based subset.")
    lines.append("It records feature dropping, missing-code recoding, row filtering, and imputation decisions.")
    lines.append("")
    lines.append("## Input and output")
    lines.append("")
    lines.append(f"- Input dataset: {input_path}")
    lines.append(f"- Final CSV output: {output_csv}")
    lines.append(f"- Initial shape: {rows_initial:,} rows x {cols_initial} columns")
    lines.append("")
    lines.append("## Step 1: Feature removed")
    lines.append("")
    lines.append("Feature dropped by project decision:")
    for feature in dropped_features:
        lines.append(f"- {feature}")
    lines.append("")
    lines.append("Reason: this feature had very high missingness and reduced usable sample size in complete-case setups.")
    lines.append("")
    lines.append("## Step 2: Recode BRFSS special missing codes")
    lines.append("")
    lines.append("Special survey codes (for example, don't know/refused) were converted to missing values (NaN) before imputation.")
    lines.append("")
    lines.append("| Column | Replaced with NaN (count) |")
    lines.append("|---|---:|")
    for col in sorted(recode_counts.keys()):
        lines.append(f"| {col} | {recode_counts[col]:,} |")
    lines.append("")
    lines.append("## Step 3: Target preparation")
    lines.append("")
    lines.append("- Source target column: has_diabetes")
    lines.append("- Binary target created: has_diabetes_binary")
    lines.append("- Mapping used: {1,2} -> 1 (positive), {3,4} -> 0 (negative)")
    lines.append("- Rows with unmapped target values were removed")
    lines.append("")
    removed = rows_before_target_filter - rows_after_target_filter
    lines.append(f"- Rows before target filtering: {rows_before_target_filter:,}")
    lines.append(f"- Rows after target filtering: {rows_after_target_filter:,}")
    lines.append(f"- Rows removed at this step: {removed:,} ({pct(removed, rows_before_target_filter)})")
    lines.append("")
    lines.append("## Step 4: Predictor imputation")
    lines.append("")
    lines.append("Imputation rule:")
    lines.append("- Numeric predictors: median imputation")
    lines.append("- Categorical predictors: mode imputation")
    lines.append("")
    lines.append("Imputation values used:")
    lines.append("")
    lines.append("| Column | Fill value |")
    lines.append("|---|---|")
    for col in sorted(fill_values.keys()):
        lines.append(f"| {col} | {fill_values[col]} |")
    lines.append("")
    lines.append("## Missingness check (before vs after imputation)")
    lines.append("")
    lines.append("| Column | Missing before | Missing after |")
    lines.append("|---|---:|---:|")
    for col in missing_before_impute.index:
        before = int(missing_before_impute[col])
        after = int(missing_after_impute[col]) if col in missing_after_impute.index else 0
        lines.append(f"| {col} | {before:,} | {after:,} |")
    lines.append("")
    lines.append("## Final recommendation for modeling")
    lines.append("")
    lines.append("- Train with has_diabetes_binary as label.")
    lines.append("- Keep both has_diabetes and has_diabetes_binary in the file for traceability.")
    lines.append("- If needed, compare this imputed dataset against a stricter complete-case baseline.")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    df = read_input(args.input_path)
    rows_initial, cols_initial = df.shape

    for col in DROP_FEATURES:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    recode_counts = recode_special_missing(df)

    rows_before_target_filter, rows_after_target_filter = build_binary_target(df)

    predictors = [c for c in df.columns if c not in {TARGET_RAW, TARGET_BINARY}]
    missing_before_impute = df[predictors].isna().sum().sort_values(ascending=False)

    fill_values = impute_predictors(df)

    missing_after_impute = df[predictors].isna().sum().sort_values(ascending=False)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output_csv, index=False)

    write_markdown_report(
        args.output_md,
        input_path=args.input_path,
        output_csv=args.output_csv,
        rows_initial=rows_initial,
        cols_initial=cols_initial,
        dropped_features=DROP_FEATURES,
        recode_counts=recode_counts,
        rows_before_target_filter=rows_before_target_filter,
        rows_after_target_filter=rows_after_target_filter,
        missing_before_impute=missing_before_impute,
        missing_after_impute=missing_after_impute,
        fill_values=fill_values,
    )

    print(f"Saved cleaned CSV to: {args.output_csv}")
    print(f"Saved process markdown to: {args.output_md}")
    print(f"Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")


if __name__ == "__main__":
    main()
