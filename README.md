[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

## Dataset
The Behavioral Risk Factor Surveillance System (BRFSS) is the largest continuously conducted health survey system in the world. It collects data on preventive health practices, risk behaviors, and chronic health conditions among U.S. adults. The 2024 dataset contains over 400,000 survey responses across 50 U.S. states and territories.

**Download the dataset:**
- [Official CDC Website (Recommended)](https://www.cdc.gov/brfss/annual_data/annual_2024.html)
- [Google Drive](https://drive.google.com/file/d/1rp-CuzP-wnhk3gEbNib1MZ5ci_r8etMw/view?usp=sharing)



## Why These Variables

We picked ~75 variables that support **three candidate prediction targets** (team
still deciding which one to go with):

| Target                | Column            | Question it answers                       |
|-----------------------|-------------------|-------------------------------------------|
| Diabetes              | `has_diabetes`    | Can we predict diabetes from risk factors? |
| Depression            | `has_depression`  | What behavioral/social factors predict it? |
| Insurance access      | `has_insurance`   | Who lacks coverage and why?               |

The predictor variables cover the main categories you'd need for any of these:

- **Demographics** — age, sex, race, income, education, employment, marital status
- **Health status** — general health, physical/mental health days
- **Chronic conditions** — heart disease, stroke, asthma, COPD, kidney disease, etc.
- **Body metrics** — BMI, height, weight
- **Lifestyle** — exercise, smoking, alcohol
- **Social determinants** — food insecurity, bills, transportation, loneliness
- **Disability** — hearing, vision, mobility, cognition
- **Healthcare access** — insurance, personal doctor, cost barriers

## Variable Reference

Full mapping from BRFSS codebook names to our clean names. Use this when cross-referencing
the [BRFSS Codebook](https://www.cdc.gov/brfss/annual_data/2024/llcp-codebook24.html).

### Survey Design
| BRFSS Code | Our Name               | Description                    |
|------------|------------------------|--------------------------------|
| `_LLCPWT`  | `survey_weight`        | Final survey weight            |
| `_STSTR`   | `stratification_var`   | Stratification variable        |
| `_PSU`     | `primary_sampling_unit`| Primary sampling unit          |

### Geography
| BRFSS Code | Our Name       | Description          |
|------------|----------------|----------------------|
| `_STATE`   | `state_fips`   | State FIPS code      |
| `_METSTAT` | `metro_status` | Metropolitan status  |
| `_URBSTAT` | `urban_rural`  | Urban/rural status   |

### Demographics
| BRFSS Code | Our Name                  | Description                      |
|------------|---------------------------|----------------------------------|
| `_SEX`     | `sex`                     | Sex (calculated)                 |
| `SEXVAR`   | `sex_raw`                 | Sex of respondent                |
| `_AGEG5YR` | `age_group_5yr`           | Age in 5-year groups             |
| `_AGE65YR` | `age_group_65`            | Age: 18–64 / 65+                |
| `_AGE80`   | `age_imputed`             | Imputed age (capped at 80)       |
| `_AGE_G`   | `age_group_6`             | Imputed age in 6 groups          |
| `_IMPRACE` | `race_ethnicity_imputed`  | Imputed race/ethnicity           |
| `_RACE`    | `race_ethnicity`          | Computed race-ethnicity          |
| `_RACEGR3` | `race_ethnicity_5lvl`     | 5-level race/ethnicity           |
| `_EDUCAG`  | `education_level`         | Education level (computed)       |
| `EDUCA`    | `education_raw`           | Education level (raw)            |
| `_INCOMG1` | `income_level`            | Income categories (computed)     |
| `INCOME3`  | `income_raw`              | Income level (raw)               |
| `MARITAL`  | `marital_status`          | Marital status                   |
| `EMPLOY1`  | `employment_status`       | Employment status                |
| `VETERAN3` | `is_veteran`              | Veteran status                   |
| `CHILDREN` | `num_children`            | Number of children in household  |
| `RENTHOM1` | `own_or_rent`             | Own or rent home                 |

### Candidate Targets
| BRFSS Code | Our Name                  | Description                          |
|------------|---------------------------|--------------------------------------|
| `DIABETE4` | `has_diabetes`            | Ever told had diabetes               |
| `DIABAGE4` | `diabetes_age_diagnosed`  | Age when first told                  |
| `PREDIAB2` | `has_prediabetes`         | Pre-diabetes status                  |
| `PDIABTS1` | `last_blood_sugar_test`   | Last blood sugar test                |
| `ADDEPEV3` | `has_depression`          | Ever told had depressive disorder    |
| `MENTHLTH` | `days_poor_mental_health` | Days mental health not good (past 30)|
| `LSATISFY` | `life_satisfaction`       | Satisfaction with life               |
| `EMTSUPRT` | `emotional_support_freq`  | How often get emotional support      |
| `SDLONELY` | `loneliness_freq`         | How often feel lonely                |
| `_HLTHPL2` | `has_insurance`           | Have any health insurance            |
| `_HCVU654` | `has_insurance_18_64`     | 18–64 with health insurance          |
| `PRIMINS2` | `insurance_type`          | Primary insurance source             |
| `PERSDOC3` | `has_personal_doctor`     | Have personal doctor                 |
| `MEDCOST1` | `cant_afford_doctor`      | Could not afford doctor              |
| `CHECKUP1` | `time_since_checkup`      | Time since last checkup              |

### Health Status
| BRFSS Code | Our Name                    | Description                            |
|------------|-----------------------------|----------------------------------------|
| `GENHLTH`  | `general_health`            | General health (1=Excellent to 5=Poor) |
| `PHYSHLTH` | `days_poor_physical_health` | Days physical health not good          |
| `POORHLTH` | `days_poor_health_overall`  | Days poor physical or mental health    |

### Chronic Conditions
| BRFSS Code | Our Name            | Description                  |
|------------|---------------------|------------------------------|
| `CVDINFR4` | `had_heart_attack`  | Ever had heart attack        |
| `CVDCRHD4` | `has_heart_disease` | Coronary heart disease       |
| `CVDSTRK3` | `had_stroke`        | Ever had stroke              |
| `ASTHMA3`  | `had_asthma`        | Ever had asthma              |
| `CHCCOPD3` | `has_copd`          | COPD / emphysema / bronchitis|
| `CHCKDNY2` | `has_kidney_disease` | Kidney disease              |
| `HAVARTH4` | `has_arthritis`     | Arthritis                    |
| `CHCSCNC1` | `has_skin_cancer`   | Skin cancer (non-melanoma)   |
| `CHCOCNC1` | `has_other_cancer`  | Melanoma / other cancer      |

### Body Metrics
| BRFSS Code | Our Name        | Description                         |
|------------|-----------------|-------------------------------------|
| `_BMI5`    | `bmi_x100`     | BMI × 100 (divide by 100 for real)  |
| `_BMI5CAT` | `bmi_category` | BMI category                        |
| `HTIN4`    | `height_inches` | Height in inches                   |
| `WTKG3`    | `weight_kg`     | Weight in kilograms                |

### Lifestyle & Behavioral
| BRFSS Code | Our Name                | Description                       |
|------------|-------------------------|-----------------------------------|
| `EXERANY2` | `exercised_past_30d`    | Any exercise past 30 days         |
| `_TOTINDA` | `any_physical_activity` | Leisure time physical activity    |
| `SMOKE100` | `smoked_100_cigs_ever`  | Smoked 100+ cigarettes ever       |
| `_SMOKER3` | `smoking_status`        | Computed smoking status           |
| `ALCDAY4`  | `alcohol_days_past_30d` | Alcohol days past 30              |
| `_RFBING6` | `is_binge_drinker`      | Binge drinking                    |
| `_RFDRHV9` | `is_heavy_drinker`      | Heavy alcohol consumption         |
| `DRNKANY6` | `any_alcohol_past_30d`  | Any alcohol past 30 days          |
| `LASTDEN4` | `last_dentist_visit`    | Last dentist visit                |
| `FLUSHOT7` | `had_flu_shot_12mo`     | Flu shot past 12 months           |

### Social Determinants
| BRFSS Code | Our Name              | Description                          |
|------------|-----------------------|--------------------------------------|
| `SDHEMPLY` | `lost_employment`     | Lost employment / reduced hours      |
| `FOODSTMP` | `receives_food_stamps`| Received food stamps past 12 months  |
| `SDHFOOD1` | `food_insecurity`     | Food didn't last / no money for more |
| `SDHBILLS` | `cant_pay_bills`      | Couldn't pay bills                   |
| `SDHUTILS` | `cant_pay_utilities`  | Couldn't pay utility bills           |
| `SDHTRNSP` | `lacks_transportation`| Lack of reliable transportation      |
| `HOWSAFE1` | `neighborhood_safety` | Neighborhood safe from crime         |

### Disability
| BRFSS Code | Our Name                  | Description                    |
|------------|---------------------------|--------------------------------|
| `DEAF`     | `difficulty_hearing`      | Serious hearing difficulty     |
| `BLIND`    | `difficulty_seeing`       | Blind or difficulty seeing     |
| `DECIDE`   | `difficulty_concentrating`| Difficulty concentrating       |
| `DIFFWALK` | `difficulty_walking`      | Difficulty walking / climbing  |
| `DIFFDRES` | `difficulty_dressing`     | Difficulty dressing / bathing  |
| `DIFFALON` | `difficulty_errands`      | Difficulty doing errands alone |

## How To Add Variables

1. Open `pipeline/Subsetting.py`
2. Find the right category dictionary (or create a new one)
3. Add an entry: `"BRFSS_CODE": "your_clean_name"`
4. If you made a new dict, add it to the `RENAME_MAP` loop
5. Re-run: `uv run python pipeline/Subsetting.py`
6. Update this README with the new variable

The BRFSS codebook is in `data/raw/` or online at the CDC site.
