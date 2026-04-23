# Diabetes Risk Data Preparation Notes

## Why this document exists

This note documents how the final training CSV was prepared from the literature-based subset.
It records feature dropping, missing-code recoding, row filtering, and imputation decisions.

## Input and output

- Input dataset: data\subsets\diabetes_risk_literature_subset.parquet
- Final CSV output: literature\diabetes_risk_literature_subset_final.csv
- Initial shape: 457,670 rows x 14 columns

## Step 1: Feature removed

Feature dropped by project decision:
- food_insecurity

Reason: this feature had very high missingness and reduced usable sample size in complete-case setups.

## Step 2: Recode BRFSS special missing codes

Special survey codes (for example, don't know/refused) were converted to missing values (NaN) before imputation.

| Column | Replaced with NaN (count) |
|---|---:|
| any_alcohol_past_30d | 43,777 |
| any_physical_activity | 1,315 |
| bmi_x100 | 0 |
| education_level | 2,363 |
| general_health | 1,305 |
| has_diabetes | 1,030 |
| height_inches | 0 |
| income_level | 87,423 |
| smoking_status | 32,022 |
| weight_kg | 0 |

## Step 3: Target preparation

- Source target column: has_diabetes
- Binary target created: has_diabetes_binary
- Mapping used: {1,2} -> 1 (positive), {3,4} -> 0 (negative)
- Rows with unmapped target values were removed

- Rows before target filtering: 457,670
- Rows after target filtering: 456,636
- Rows removed at this step: 1,034 (0.23%)

## Step 4: Predictor imputation

Imputation rule:
- Numeric predictors: median imputation
- Categorical predictors: mode imputation

Imputation values used:

| Column | Fill value |
|---|---|
| any_alcohol_past_30d | mode=1.0 |
| any_physical_activity | mode=1.0 |
| bmi | median=27.44 |
| bmi_x100 | median=2744.0 |
| education_level | mode=4.0 |
| general_health | mode=3.0 |
| height_inches | median=67.0 |
| income_level | mode=5.0 |
| smoking_status | mode=4.0 |
| weight_kg | median=8074.0 |

## Missingness check (before vs after imputation)

| Column | Missing before | Missing after |
|---|---:|---:|
| income_level | 86,930 | 0 |
| any_alcohol_past_30d | 43,534 | 0 |
| bmi | 42,723 | 0 |
| bmi_x100 | 42,723 | 0 |
| weight_kg | 36,120 | 0 |
| smoking_status | 31,813 | 0 |
| height_inches | 31,546 | 0 |
| education_level | 2,249 | 0 |
| general_health | 1,252 | 0 |
| any_physical_activity | 1,243 | 0 |
| age_imputed | 0 | 0 |
| sex | 0 | 0 |

## Final recommendation for modeling

- Train with has_diabetes_binary as label.
- Keep both has_diabetes and has_diabetes_binary in the file for traceability.
- If needed, compare this imputed dataset against a stricter complete-case baseline.