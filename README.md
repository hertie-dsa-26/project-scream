[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# SCREAM: Diabetes Risk Predictor

*(🚀 **Live Demo coming soon:** We plan to deploy the app for free continuous access. Check back later for the link!)*

SCREAM is an interactive web application that uses machine learning to estimate an individual's risk of developing diabetes based on behavioral, demographic, and health factors. Our predictive models are powered by the 2024 Behavioral Risk Factor Surveillance System (BRFSS) dataset from the CDC.

For full technical documentation — architecture, model details, key files, and notes for graders — see [`DOCS.md`](DOCS.md).

---

## Setup & Installation

**Prerequisites:**
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (our chosen Python package manager)

**1. Clone the repository and install dependencies:**
```bash
git clone https://github.com/hertie-dsa-26/project-scream.git
cd project-scream
uv sync
```

**2. Data requirements:**
The BRFSS parquet is not committed to the repository (too large). Place it at:
```
data/subsets/brfss2024_subset.parquet
```
Download links:
- [Official CDC Website](https://www.cdc.gov/brfss/annual_data/annual_2024.html)
- [Google Drive Mirror](https://drive.google.com/file/d/1rp-CuzP-wnhk3gEbNib1MZ5ci_r8etMw/view?usp=sharing)

The parquet is required for the home page map and explorer charts. Predictions will work without it since the model artifacts are pre-trained and committed.

**3. Run the app:**
```bash
uv run flask --app run.py run --debug
```
The app will be available at `http://127.0.0.1:5000`.

**4. Run the tests:**
```bash
uv run pytest tests/ -v
```
Tests that require the BRFSS parquet are skipped automatically if the file is not present.

**5. Retraining the model (if needed):**
The trained SVM artifacts are committed to `app/model/artifacts/` and do not need to be regenerated unless you change the training data or sklearn version. If you do need to retrain:
```bash
uv run python retrain_svm.py
```

---

## Features

- **Personalised risk prediction:** Users submit health factors via an intuitive form — including height and weight (metric or imperial), age, lifestyle and socioeconomic indicators — to receive a tailored diabetes risk score and category (low / moderate / high).
- **Actionable health suggestions:** Dynamic recommendations based on counterfactual modelling — e.g. how switching from inactive to active would shift the user's estimated score.
- **Data explorer:** An interactive dashboard exploring relationships between demographic and lifestyle factors and diabetes prevalence across the U.S., with the user's position highlighted on each chart based on their last prediction.
- **Scrollytelling home page:** A narrative map-driven landing page showing state-level diabetes prevalence computed directly from the BRFSS dataset, with animated zoom to the southern belt.
- **Detailed breakdown:** Feature weight visualisation, population benchmarks, CDC resources, and full literature citations on the details page.

---

## Data & Methodology

The model is trained on a subset of ~450,000 responses from the **2024 BRFSS**, using 9 features covering demographics, lifestyle, and general health.

**Model:** A from-scratch linear SVM (`ManualSVM`) implemented in `app/utils/model.py` using SGD with hinge loss. This satisfies the course requirement for a custom algorithm implementation. Risk scoring uses sigmoid(decision score) since the SVM has no `predict_proba`. The model achieves ROC-AUC ~0.78 on the held-out test set.

**Features used:**
- General health self-rating
- Physical activity (past 30 days)
- Sex
- Age
- BMI (computed from height and weight)
- Education level
- Income level
- Smoking status
- Alcohol use (past 30 days)

---

## Architecture

The application follows a modular structure with strict separation of concerns:

- **`app/routes/`** — HTTP endpoints only; no business logic
- **`app/utils/`** — core logic: input validation, model inference, data aggregation
- **`app/model/artifacts/`** — pre-trained SVM, scaler, and feature columns
- **`app/templates/`** — Jinja2 templates with Plotly.js for interactive charts
- **`tests/`** — 75 pytest tests with GitHub Actions CI
- **`pipeline/`** — scripts for subsetting and processing raw BRFSS data

See [`DOCS.md`](DOCS.md) for a full directory tree, request flow walkthrough, and key file reference.

---

## Literature

Machine learning approaches applied to diabetes prediction using demographic and lifestyle features have been extensively studied. The following research informed our methodology:

1. *A Comparative Study of Diabetes Prediction Based on Lifestyle Factors Using Machine Learning.* Diagnostics (MDPI). [Link](https://www.mdpi.com/2075-4418/15/20/2622)
2. *AI-driven analysis of diabetes risk determinants in US adults: Exploring disease prevalence and health factors.* ResearchGate. [Link](https://www.researchgate.net/publication/395238407_AI-driven_analysis_of_diabetes_risk_determinants_in_US_adults_Exploring_disease_prevalence_and_health_factors)
3. *Diabetes Prediction Using Feature Selection Algorithms and Boosting-Based Machine Learning Classifiers.* ResearchGate. [Link](https://www.researchgate.net/publication/396643677_Diabetes_Prediction_Using_Feature_Selection_Algorithms_and_Boosting-Based_Machine_Learning_Classifiers)
4. *Identification of key cardiovascular disease predictive factors from the China Health and Retirement Longitudinal Study dataset using machine learning-based algorithms.* ResearchGate. [Link](https://www.researchgate.net/publication/401155832)
5. *Cardiovascular and Diabetes Diseases Classification Using Ensemble Stacking Classifiers with SVM as a Meta Classifier.* ResearchGate. [Link](https://www.researchgate.net/publication/364739441)
6. *Diabetes prediction research.* PubMed Central, PMC12669510. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC12669510/)
7. *Diabetes prediction research.* PubMed Central, PMC10107388. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC10107388/)
8. *Diabetes prediction research.* BMJ Open, e096595. [Link](https://bmjopen.bmj.com/content/15/3/e096595)

---

## Meet the Team

This project was built collaboratively by Team SCREAM:

- **Adarsh Tripathi**
- **David Colín**
- **Jesper Boon**
- **Kevine Shima**
- **Luis Czajka**
- **Marcell Matei**
- **Yenus Ibrahim Ayalew**
