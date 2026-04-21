# Diabetes Risk Literature Synthesis 

## Important note before reading

We found 2 files that appear to be the same paper:

- `1-LTR-India-diabetus.pdf`
- `Diabetes prediction using machine learning.pdf`

To avoid confusion and double counting, the detailed summary below keeps only one canonical entry for this paper.

## Why this document exists

This note is designed to help model building.
It focuses on:

- what approaches are repeatedly used,
- what results are actually common,
- what mistakes we should avoid,
- what is still missing in our current understanding,
- and quick paper-level highlights for fast onboarding.

## Scope of papers reviewed

Reviewed documents in `literature/`:

1. `1-LTR-India-diabetus.pdf`
2. `2-LR-diabtus.pdf`
3. `3-LR-BFRSS.pdf`
4. `4-LR-_brfss_diabetes.pdf`
5. `Chen et. al (2025) Machine learnign model to predict Cardiovascular diseases based on Diabetes.pdf`
6. `Khan et.al (2024) Cardiovascular and Diabetes Classification using Ensamble Stacking Classifiers with SVM.pdf`
7. `Learning from the machine is diabetes in adults predicted by lifestyle variables.pdf`

Duplicate handling: `Diabetes prediction using machine learning.pdf` is treated as a duplicate of `1-LTR-India-diabetus.pdf` and is excluded from separate detailed analysis.

---

## What approaches most papers used

### 1) Supervised tabular ML dominates

Most studies compare classic tabular classifiers:

- Logistic Regression
- Decision Tree
- Random Forest
- SVM
- KNN
- Gradient Boosting variants (XGBoost/LightGBM/CatBoost)

### 2) Ensemble methods are repeatedly favored

Two repeated ensemble styles:

- Boosting (especially XGBoost/Gradient Boosting)
- Stacking (base learners + meta-classifier)

### 3) Class imbalance handling appears frequently

- SMOTE and ADASYN are common.
- Several papers report stronger minority-class detection after rebalancing.

### 4) Feature engineering/selection is important

- Logistic/Lasso/RFE-based feature selection appears in stronger studies.
- Better feature pipelines are often as important as model choice.

### 5) Explainability is increasingly included

- SHAP/LIME are used in newer papers (especially BRFSS/NHANES style work).
- This is important for health decision support, not just model accuracy.

---

## Common learnings across papers

### 1) No single model always wins, but boosting is consistently strong

- XGBoost or Gradient Boosting repeatedly performs near the top.
- Random Forest is often a robust baseline and sometimes best on smaller/cleaner datasets.

### 2) Reported accuracy can be misleading in imbalanced health data

- Papers with high specificity and moderate-to-low sensitivity show that "good accuracy" can still miss positive cases.
- For diabetes risk screening, missing true positives can be costly.

### 3) Data quality and variable design matter more than algorithm novelty

- Better feature coverage (lifestyle + anthropometrics + clinical risk factors) and missing-data handling improve practical performance.

### 4) Practical deployment is feasible

- Some studies deploy web/mobile prototypes, showing this can become a usable product artifact, not only an academic model.

---

## Pitfalls we should avoid

### 1) Over-focusing on one metric

Do not optimize only accuracy. Always evaluate:

- AUROC
- PR-AUC
- Sensitivity/Recall
- Specificity
- Precision
- F1
- Calibration (very important for probability outputs)

### 2) Ignoring probability calibration

Our project goal is probability (% risk), so raw classifier scores are not enough.

We should calibrate probabilities (for example: Platt scaling or isotonic regression) and validate calibration curves/Brier score.

### 3) Dataset leakage and weak validation

- Avoid random leakage through preprocessing outside CV folds.
- Use train/validation/test separation with pipeline-safe transformations.
- Prefer repeated CV and external holdout checks.

### 4) Poor handling of class imbalance

- If prevalence is low, accuracy can look high while recall is poor.
- Rebalancing and threshold tuning should be done carefully and only on training folds.

### 5) Under-reporting subgroup fairness/performance

- Diabetes risk differs by age, income, race/ethnicity, sex, and access factors.
- We should report subgroup metrics to avoid a model that works well only for majority groups.

### 6) Using non-representative data without caveats

- Pima-only pipelines may not transfer well to BRFSS-like public health settings.
- Population mismatch can break generalization.

---

## What seems missing from our current understanding (important gaps)

### 1) Probability quality, not only discrimination

Many studies emphasize ranking metrics (AUC) but do not deeply validate probability calibration.
For our artifact, calibrated and trustworthy probability estimates are essential.

### 2) Decision-threshold strategy for real use

Most papers report model scores but not how to choose risk thresholds for actions.
We should predefine threshold bands, for example:

- low risk,
- moderate risk,
- high risk,

based on sensitivity/specificity tradeoffs and stakeholder needs.

### 3) Survey-aware modeling for BRFSS-like data

When using survey datasets, weighting/representativeness and prevalence shifts need explicit treatment.

### 4) Prospective validation

Most studies are retrospective; very few test temporal robustness.
If possible, we should test stability across time splits.

### 5) Communication layer for non-technical users

Even with good models, user trust requires plain-language risk explanations.
Our final artifact should combine probability + key drivers + actionable next step text.

---

## Paper-by-paper brief descriptions and highlights

## 1) `1-LTR-India-diabetus.pdf` (canonical copy for the duplicate pair)

- Focus: diabetes prediction using Pima + small private female cohort from Bangladesh.
- Methods: DT, SVM, RF, LR, KNN, ensembles; SMOTE/ADASYN; SHAP/LIME.
- Highlight result: best reported setup was XGBoost + ADASYN, with around Accuracy 81%, F1 0.81, AUC 0.84.
- Useful idea for us: combine imbalance handling + explainability + deployment prototype.
- Caution: small private sample (203) and transferability limits.

## 2) `2-LR-diabtus.pdf`

- Focus: female-only diabetes prediction on PIMA dataset.
- Methods: RF, DT, Naive Bayes, Logistic Regression, with EDA/PCA workflow.
- Highlight result: RF reported best overall (around Accuracy 80%, Precision 82%, Sensitivity 88% in paper summary).
- Useful idea for us: strong baseline benchmarking with simple, interpretable models first.
- Caution: narrow population and potential limited generalization.

## 3) `3-LR-BFRSS.pdf`

- Focus: explainable ML for self-reported diabetes in Tennessee BRFSS 2023.
- Methods: Logistic, SVM, KNN, DT, RF, Gradient Boosting, XGBoost + SHAP.
- Highlight result: Gradient Boosting performed best overall (reported Accuracy 82%, AUROC 0.80, PR-AUC 0.45, but moderate recall).
- Useful idea for us: real-world public health predictors + SHAP for policy/interpretation.
- Caution: self-reported outcome and class-imbalance effects (precision/recall tradeoff).

## 4) `4-LR-_brfss_diabetes.pdf`

- Focus: surveillance brief, not a predictive ML model.
- Value: gives prevalence and disparity context (income, education, obesity, disability, age, race/ethnicity).
- Useful idea for us: informs feature framing and subgroup reporting requirements.
- Caution: cannot be used as a model-performance benchmark.

## 5) `Chen et. al (2025) Machine learnign model to predict Cardiovascular diseases based on Diabetes.pdf`

- Focus: among T2DM patients, predict CHD comorbidity risk.
- Methods: logistic/lasso/RFE feature selection + SVM/RF/XGBoost/LightGBM modeling.
- Highlight result: optimized XGBoost model reported around AUC 0.814, Accuracy 0.799, Recall 0.920, F1 0.879.
- Useful idea for us: rigorous feature-selection plus model comparison pipeline.
- Caution: this is a CHD-in-T2DM task, not pure diabetes onset risk.

## 6) `Khan et.al (2024) Cardiovascular and Diabetes Classification using Ensamble Stacking Classifiers with SVM.pdf`

- Focus: ensemble stacking for diabetes and cardiovascular classification.
- Methods: base learners (KNN, NB, DT, LDA), meta-classifier (SVM or RF, task-dependent).
- Highlight result: very high reported diabetes accuracy (~0.9735) and improved cardiovascular classification versus single models.
- Useful idea for us: stacking can improve performance over single models.
- Caution: very high scores require strict leakage checks and robust external validation before trusting.

## 7) `Learning from the machine is diabetes in adults predicted by lifestyle variables.pdf`

- Focus: non-invasive diabetes risk prediction in US adults (NHANES 2007-2018; n ~29,509).
- Methods: logistic, SVM, RF, XGBoost, CatBoost; cross-validation and feature analysis.
- Highlight result: XGBoost had best discrimination (AUC ~0.8168); many models showed high specificity, sensitivity varied.
- Useful idea for us: relevant design for user-facing risk screening without lab tests.
- Caution: self-reported diabetes and cross-sectional design limit causal claims.

---

## Feature check against our current data and product goal

We currently have a broad BRFSS-based feature set (demographics, lifestyle, body metrics, social determinants, disability, healthcare access, and chronic-condition history).

Since our product goal is: "ask basic user information and return diabetes risk probability", we should split features into practical tiers.

## A) Features to use in the basic user form (recommended first release)

These are easy for most users to answer and aligned with patterns seen in NHANES/BRFSS literature.

- `age_group_5yr` or `age_imputed`
- `sex`
- `height_inches` and `weight_kg` (or compute from one BMI input)
- `any_physical_activity` or `exercised_past_30d`
- `smoking_status`
- `any_alcohol_past_30d`
- `general_health`
- `education_level`
- `income_level` (allow "prefer not to answer")
- `food_insecurity` (optional if user experience allows)

Why this set: papers consistently show lifestyle, anthropometric, and sociodemographic variables are useful for non-invasive early screening.

## B) Features to test in model training, but keep optional in user form

These can add predictive power, but may increase friction or feel sensitive for users.

- `has_personal_doctor`, `cant_afford_doctor`, `has_insurance`
- `employment_status`, `own_or_rent`
- `difficulty_walking`, `difficulty_seeing`, `difficulty_hearing`
- `days_poor_physical_health`, `days_poor_mental_health`

Product suggestion: ask these only in an "advanced assessment" mode, not in the first short questionnaire.

## C) Features to exclude from diabetes risk prediction target model

Exclude these from the diabetes risk model to avoid leakage or circularity:

- `has_diabetes` (this is the target label)
- `diabetes_age_diagnosed` (post-diagnosis information)
- `last_blood_sugar_test` (testing behavior can leak diagnosis/access patterns)
- `has_prediabetes` (very close to the target concept; can dominate and reduce usefulness for early discovery)

Also do not use survey design variables as user-level predictors:

- `survey_weight`, `stratification_var`, `primary_sampling_unit`

These are for survey inference weighting, not personal risk questionnaire inputs.

## D) What literature suggests about leaving features out

Based on reviewed papers and our goal, we should leave out features when they are:

- Hard for users to answer reliably in a short form.
- Too sensitive for first contact (unless optional).
- Clearly post-diagnosis or near-label leakage.
- Weakly actionable for prevention messaging.

This keeps the tool practical while preserving predictive value.

## E) Suggested user input design (simple and clear)

Use a short first-step form (8-12 questions), then return:

1. Risk probability percentage.
2. Risk band (low, moderate, high).
3. Top 3-5 contributing factors in plain language.
4. A short "what to do next" message.

Example flow:

- Step 1: basic profile and lifestyle questions.
- Step 2: optional advanced questions for refined probability.
- Step 3: calibrated risk output plus explanation.

This follows the strongest pattern from NHANES/BRFSS-style papers: non-invasive risk screening with explainability.

---

## Practical guidance for our next modeling sprint

Recommended baseline experiment bundle for our team:

1. Baselines: Logistic Regression, Random Forest, XGBoost.
2. Optional advanced: LightGBM/CatBoost + one stacking model.
3. Evaluation: AUROC, PR-AUC, precision, recall, F1, specificity, calibration (Brier + reliability curve).
4. Validation: stratified CV + untouched holdout set.
5. Imbalance: class weights and/or SMOTE inside CV folds only.
6. Explainability: SHAP summary + top-feature direction table.
7. Output format: calibrated probability (%) + plain-language risk band.

Additional implementation note for this project:

8. Train two versions and compare:
	- Version A: basic-user features only.
	- Version B: basic + optional advanced features.
	Choose default deployment based on the best tradeoff between usability and model performance.

This makes the work review-friendly for the professor and execution-ready for team model training.
