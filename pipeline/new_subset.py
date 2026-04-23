"""Create a diabetes-risk subset from BRFSS 2024 using literature-recommended features.

Usage examples:
    uv run python pipeline/new_subset.py
    uv run python pipeline/new_subset.py --basic-only
    uv run python pipeline/new_subset.py --out-path data/subsets/my_subset.parquet
    uv run python pipeline/new_subset.py --basic-only --save-csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pyreadstat


# Target label for diabetes risk prediction.
TARGET = {
    "DIABETE4": "has_diabetes",
}


# Literature-recommended first-release features (short questionnaire).
BASIC_FEATURES = {
    "_AGE80": "age_imputed",
    "_SEX": "sex",
    "HTIN4": "height_inches",
    "WTKG3": "weight_kg",
    "_BMI5": "bmi_x100",
    "_TOTINDA": "any_physical_activity",
    "_SMOKER3": "smoking_status",
    "DRNKANY6": "any_alcohol_past_30d",
    "GENHLTH": "general_health",
    "_EDUCAG": "education_level",
    "_INCOMG1": "income_level",
    "SDHFOOD1": "food_insecurity",
}


# Literature-recommended optional advanced features.
ADVANCED_FEATURES = {
    "PERSDOC3": "has_personal_doctor",
    "MEDCOST1": "cant_afford_doctor",
    "_HLTHPL2": "has_insurance",
    "EMPLOY1": "employment_status",
    "RENTHOM1": "own_or_rent",
    "DIFFWALK": "difficulty_walking",
    "BLIND": "difficulty_seeing",
    "DEAF": "difficulty_hearing",
    "PHYSHLTH": "days_poor_physical_health",
    "MENTHLTH": "days_poor_mental_health",
}


DEFAULT_XPT_PATH = Path("data/raw/LLCP2024.XPT")
DEFAULT_OUT_PATH = Path("data/subsets/diabetes_risk_literature_subset.parquet")
ENCODING_CANDIDATES = (None, "latin1", "cp1252")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Subset BRFSS 2024 to diabetes-risk features from the literature synthesis."
    )
    parser.add_argument(
        "--xpt-path",
        type=Path,
        default=DEFAULT_XPT_PATH,
        help=f"Path to BRFSS XPT file (default: {DEFAULT_XPT_PATH})",
    )
    parser.add_argument(
        "--out-path",
        type=Path,
        default=DEFAULT_OUT_PATH,
        help=f"Output parquet path (default: {DEFAULT_OUT_PATH})",
    )
    parser.add_argument(
        "--basic-only",
        action="store_true",
        help="Keep only target + basic features (skip advanced optional features).",
    )
    parser.add_argument(
        "--save-csv",
        action="store_true",
        help="Also save a CSV copy for easier sharing (for example with Colab).",
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=None,
        help="Optional CSV output path. Defaults to --out-path with .csv extension.",
    )
    return parser.parse_args()


def build_rename_map(include_advanced: bool) -> dict[str, str]:
    rename_map: dict[str, str] = {}
    rename_map.update(TARGET)
    rename_map.update(BASIC_FEATURES)
    if include_advanced:
        rename_map.update(ADVANCED_FEATURES)
    return rename_map


def read_xport_with_fallback(
    xpt_path: Path, *, metadataonly: bool = False, usecols: list[str] | None = None
) -> tuple[pd.DataFrame, pyreadstat._readstat_parser.metadata_container, str]:
    last_error: Exception | None = None

    for encoding in ENCODING_CANDIDATES:
        try:
            kwargs: dict[str, object] = {"metadataonly": metadataonly}
            if usecols is not None:
                kwargs["usecols"] = usecols
            if encoding is not None:
                kwargs["encoding"] = encoding

            df, meta = pyreadstat.read_xport(str(xpt_path), **kwargs)
            return df, meta, encoding or "default"
        except Exception as exc:  # Try next encoding for mixed-encoded XPT metadata.
            last_error = exc

    assert last_error is not None
    raise RuntimeError(
        "Failed to read XPT file with supported encodings. "
        f"Tried: {', '.join(str(enc or 'default') for enc in ENCODING_CANDIDATES)}"
    ) from last_error


def get_present_columns(xpt_path: Path, requested_cols: list[str]) -> tuple[list[str], list[str]]:
    _, meta, _ = read_xport_with_fallback(xpt_path, metadataonly=True)
    available = set(meta.column_names)

    present = [col for col in requested_cols if col in available]
    missing = [col for col in requested_cols if col not in available]
    return present, missing


def main() -> None:
    args = parse_args()

    if not args.xpt_path.exists():
        raise FileNotFoundError(
            f"XPT file not found: {args.xpt_path}. "
            "Update --xpt-path or place the dataset at data/raw/LLCP2024.XPT"
        )

    include_advanced = not args.basic_only
    rename_map = build_rename_map(include_advanced=include_advanced)
    requested_cols = list(rename_map.keys())

    present_cols, missing_cols = get_present_columns(args.xpt_path, requested_cols)
    if not present_cols:
        raise ValueError("None of the requested columns were found in the XPT file.")

    if missing_cols:
        print("Warning: These requested BRFSS columns were not found and will be skipped:")
        print("  " + ", ".join(missing_cols))

    print(f"Reading {len(present_cols)} columns from {args.xpt_path}...")
    df, _, used_encoding = read_xport_with_fallback(args.xpt_path, usecols=present_cols)

    effective_rename = {col: rename_map[col] for col in present_cols}
    df.rename(columns=effective_rename, inplace=True)

    if "bmi_x100" in df.columns:
        df["bmi"] = pd.to_numeric(df["bmi_x100"], errors="coerce") / 100.0

    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out_path, index=False)

    print(f"Saved subset to: {args.out_path}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Mode: {'basic-only' if args.basic_only else 'basic+advanced'}")
    print(f"Encoding used: {used_encoding}")

    if args.save_csv:
        csv_path = args.csv_path if args.csv_path is not None else args.out_path.with_suffix(".csv")
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"Saved CSV copy to: {csv_path}")

    if "has_diabetes" in df.columns:
        print("\nTarget distribution (has_diabetes):")
        print(df["has_diabetes"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()