import pyreadstat
import pandas as pd
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────
XPT_PATH = "data/raw/LLCP2024.XPT"
OUT_PATH = "data/subsets/brfss2024_subset.parquet"

# ── VARIABLE SELECTION & RENAME ─────────────────────────────────────────
# Format: { "BRFSS_CODE": "clean_name" }
# Organized by role so your team can easily add/remove groups.

# Survey design (ALWAYS keep these for weighted analysis)
SURVEY_DESIGN = {
    "_LLCPWT":   "survey_weight",
    "_STSTR":    "stratification_var",
    "_PSU":      "primary_sampling_unit",
}

# Geography
GEO = {
    "_STATE":    "state_fips",
    "_METSTAT":  "metro_status",
    "_URBSTAT":  "urban_rural",
}

# Demographics
DEMOGRAPHICS = {
    "_SEX":      "sex",
    "SEXVAR":    "sex_raw",
    "_AGEG5YR":  "age_group_5yr",
    "_AGE65YR":  "age_group_65",
    "_AGE80":    "age_imputed",
    "_AGE_G":    "age_group_6",
    "_IMPRACE":  "race_ethnicity_imputed",
    "_RACE":     "race_ethnicity",
    "_RACEGR3":  "race_ethnicity_5lvl",
    "_EDUCAG":   "education_level",
    "EDUCA":     "education_raw",
    "_INCOMG1":  "income_level",
    "INCOME3":   "income_raw",
    "MARITAL":   "marital_status",
    "EMPLOY1":   "employment_status",
    "VETERAN3":  "is_veteran",
    "CHILDREN":  "num_children",
    "RENTHOM1":  "own_or_rent",
}

# ── CANDIDATE PREDICTION TARGETS ───────────────────────────────────────

# Target A: Diabetes
DIABETES = {
    "DIABETE4":  "has_diabetes",            # ← TARGET
    "DIABAGE4":  "diabetes_age_diagnosed",
    "PREDIAB2":  "has_prediabetes",
    "PDIABTS1":  "last_blood_sugar_test",
}

# Target B: Depression / mental health
MENTAL_HEALTH = {
    "ADDEPEV3":  "has_depression",          # ← TARGET
    "MENTHLTH":  "days_poor_mental_health",
    "LSATISFY":  "life_satisfaction",
    "EMTSUPRT":  "emotional_support_freq",
    "SDLONELY":  "loneliness_freq",
}

# Target C: Health care access
HEALTHCARE_ACCESS = {
    "_HLTHPL2":  "has_insurance",           # ← TARGET
    "_HCVU654":  "has_insurance_18_64",
    "PRIMINS2":  "insurance_type",
    "PERSDOC3":  "has_personal_doctor",
    "MEDCOST1":  "cant_afford_doctor",
    "CHECKUP1":  "time_since_checkup",
}

# ── KEY FEATURES (predictors for any target) ───────────────────────────

# General health
HEALTH_STATUS = {
    "GENHLTH":   "general_health",
    "PHYSHLTH":  "days_poor_physical_health",
    "POORHLTH":  "days_poor_health_overall",
}

# Chronic conditions
CHRONIC_CONDITIONS = {
    "CVDINFR4":  "had_heart_attack",
    "CVDCRHD4":  "has_heart_disease",
    "CVDSTRK3":  "had_stroke",
    "ASTHMA3":   "had_asthma",
    "CHCCOPD3":  "has_copd",
    "CHCKDNY2":  "has_kidney_disease",
    "HAVARTH4":  "has_arthritis",
    "CHCSCNC1":  "has_skin_cancer",
    "CHCOCNC1":  "has_other_cancer",
}

# Body metrics
BODY_METRICS = {
    "_BMI5":     "bmi_x100",        # divide by 100 for actual BMI
    "_BMI5CAT":  "bmi_category",
    "HTIN4":     "height_inches",
    "WTKG3":     "weight_kg",
}

# Lifestyle & behavioral risk factors
LIFESTYLE = {
    "EXERANY2":  "exercised_past_30d",
    "_TOTINDA":  "any_physical_activity",
    "SMOKE100":  "smoked_100_cigs_ever",
    "_SMOKER3":  "smoking_status",
    "ALCDAY4":   "alcohol_days_past_30d",
    "_RFBING6":  "is_binge_drinker",
    "_RFDRHV9":  "is_heavy_drinker",
    "DRNKANY6":  "any_alcohol_past_30d",
    "LASTDEN4":  "last_dentist_visit",
    "FLUSHOT7":  "had_flu_shot_12mo",
}

# Social determinants of health
SOCIAL_DETERMINANTS = {
    "SDHEMPLY":  "lost_employment",
    "FOODSTMP":  "receives_food_stamps",
    "SDHFOOD1":  "food_insecurity",
    "SDHBILLS":  "cant_pay_bills",
    "SDHUTILS":  "cant_pay_utilities",
    "SDHTRNSP":  "lacks_transportation",
    "HOWSAFE1":  "neighborhood_safety",
}

# Disability
DISABILITY = {
    "DEAF":      "difficulty_hearing",
    "BLIND":     "difficulty_seeing",
    "DECIDE":    "difficulty_concentrating",
    "DIFFWALK":  "difficulty_walking",
    "DIFFDRES":  "difficulty_dressing",
    "DIFFALON":  "difficulty_errands",
}

# ── COMBINE ALL ─────────────────────────────────────────────────────────
ALL_GROUPS = [
    SURVEY_DESIGN, GEO, DEMOGRAPHICS,
    DIABETES, MENTAL_HEALTH, HEALTHCARE_ACCESS,
    HEALTH_STATUS, CHRONIC_CONDITIONS, BODY_METRICS,
    LIFESTYLE, SOCIAL_DETERMINANTS, DISABILITY,
]

# Merge all dicts: { BRFSS_CODE: clean_name }
RENAME_MAP = {}
for group in ALL_GROUPS:
    RENAME_MAP.update(group)

ALL_VARS = list(RENAME_MAP.keys())

# ── READ & EXPORT ───────────────────────────────────────────────────────
def main():
    xpt = Path(XPT_PATH)
    if not xpt.exists():
        print(f"ERROR: File not found: {xpt.resolve()}")
        print("Update XPT_PATH at the top of this script.")
        return

    print(f"Reading {len(ALL_VARS)} variables from {XPT_PATH}...")
    df, meta = pyreadstat.read_xport(str(xpt), usecols=ALL_VARS)

    # Rename columns
    df.rename(columns=RENAME_MAP, inplace=True)

    print(f"  Rows:    {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Memory:  {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

    # Save to Parquet
    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    parquet_size = Path(OUT_PATH).stat().st_size / 1e6
    print(f"\nSaved to {OUT_PATH} ({parquet_size:.1f} MB)")

    # Quick sanity check — print candidate targets
    print("\n── Candidate Targets ──")
    for label, col in [
        ("Diabetes",      "has_diabetes"),
        ("Depression",     "has_depression"),
        ("No Insurance",   "has_insurance"),
    ]:
        if col in df.columns:
            print(f"\n  {label} ({col}):")
            print(df[col].value_counts(dropna=False).to_string().replace("\n", "\n    "))

    # Print rename mapping for reference
    print("\n── Column Mapping (BRFSS → Clean) ──")
    for brfss, clean in RENAME_MAP.items():
        label = meta.column_names_to_labels.get(brfss, "")
        print(f"  {brfss:20s} → {clean:30s}  {label}")


if __name__ == "__main__":
    main()
