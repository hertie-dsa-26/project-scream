[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# SCREAM: Diabetes Risk Predictor

*(🚀 **Live Demo coming soon:** We plan to deploy the app for free continuous access. Check back later for the link!)*

SCREAM is an interactive web application that uses machine learning to estimate an individual's risk of developing diabetes based on behavioral, demographic, and health factors. Our predictive models are powered by the 2024 Behavioral Risk Factor Surveillance System (BRFSS) dataset from the CDC.

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

**2. Data Requirements:**
To train the model, run predictions, or view the Explorer, you must have the dataset subset locally.
* Place the `brfss2024_subset.parquet` file inside `data/subsets/`.

**3. Generate Model Artifacts:**
Because the model artifacts are not stored in version control, you must generate them locally before starting the app:
```bash
uv run python train_model.py
```
*(This will generate `pipeline.joblib`, `metrics.json`, and `coefficients.json` in `app/model/artifacts/`)*

**4. Run the Flask App:**
Start the development server:
```bash
uv run flask --app run.py run --debug
```
The app will now be accessible at `http://127.0.0.1:5000/`.

**5. Running Tests (Optional):**
To execute the robust test suite (data models, validation factors), run:
```bash
uv run pytest tests/ -v
```

## Features

- **Personalized Risk Prediction:** Users submit health factors via an intuitive UI to receive a tailored diabetes risk probability and categorization.
- **Actionable Health Suggestions:** Provides dynamic counterfactual recommendations (e.g., stopping smoking, improving physical activity) indicating exactly how lifestyle adjustments can lower the user's personal risk score.
- **Data Explorer:** An interactive dashboard exploring relationships between demographic/lifestyle factors and diabetes prevalence across the U.S.

## Data & Methodology

The model is trained on a ~400,000-response dataset from the **2024 BRFSS**, using approximately 75 variables filtering for demographics, general health, chronic conditions, lifestyle, and social determinants. We trained a **Support Vector Machine (SVM)** pipeline integrated tightly with a Flask backend.

**Download the raw dataset:**
- [Official CDC Website](https://www.cdc.gov/brfss/annual_data/annual_2024.html)
- [Google Drive Mirror](https://drive.google.com/file/d/1rp-CuzP-wnhk3gEbNib1MZ5ci_r8etMw/view?usp=sharing)

*(Note: Data dictionaries mapping BRFSS codebooks to pipeline features were utilized internally during the EDA phase.)*

## Architecture & Code Structure

The application follows a highly modular structure with clear separation of concerns:
- **`app/routes/`**: Handles the web endpoints, rendering views, and coordinating application logic.
- **`app/utils/`**: Core logic including robust input validation (`validation.py`), model ingestion (`model.py`), and data processing.
- **`app/model/artifacts/`**: Stores the locally generated machine learning pipeline models.
- **`tests/`**: A robust Pytest suite combined with GitHub Actions CI ensuring quality check coverage against regressions, validations, and bounds limits.
- **`pipeline/`**: Contains scripts for sub-setting and processing raw BRFSS data.

## Literature & Credibility

Papers where machine learning was used to predict diabetes using similar features:

1. [MDPI: A Comparative Study of Diabetes Prediction Based on Lifestyle Factors...](https://www.mdpi.com/2075-4418/15/20/2622) / [ResearchGate Version](https://www.researchgate.net/publication/389648378_A_Comparative_Study_of_Diabetes_Prediction_Based_on_Lifestyle_Factors_Using_Machine_Learning)
2. [ResearchGate: AI-driven analysis of diabetes risk determinants in US adults...](https://www.researchgate.net/publication/395238407_AI-driven_analysis_of_diabetes_risk_determinants_in_US_adults_Exploring_disease_prevalence_and_health_factors#:~:text=BMI%2C%20age%2C%20general%2C%20health%20status%2C%20income%2C%20physical%20health%20days%2C%20and%20education%20as%20those%20reporting%20poor%20general%20health)
3. [PMC: The survey's comprehensive scope includes...](https://pmc.ncbi.nlm.nih.gov/articles/PMC12669510/#:~:text=The%20survey's%20comprehensive%20scope%20includes,11)
4. [ResearchGate: Diabetes Prediction Using Feature Selection Algorithms and Boosting-Based Machine Learning Classifiers](https://www.researchgate.net/publication/396643677_Diabetes_Prediction_Using_Feature_Selection_Algorithms_and_Boosting-Based_Machine_Learning_Classifiers)
5. [ResearchGate: Identification of key cardiovascular disease predictive factors from the China Health and Retirement Longitudinal Study...](https://www.researchgate.net/publication/401155832_Identification_of_key_cardiovascular_disease_predictive_factors_from_the_China_Health_and_Retirement_Longitudinal_Study_dataset_using_machine_learning-based_algorithms)
6. [PMC10107388](https://pmc.ncbi.nlm.nih.gov/articles/PMC10107388/)
7. [ResearchGate: Cardiovascular and Diabetes Diseases Classification Using Ensemble Stacking Classifiers with SVM...](https://www.researchgate.net/publication/364739441_Cardiovascular_and_Diabetes_Diseases_Classification_Using_Ensemble_Stacking_Classifiers_with_SVM_as_a_Meta_Classifier)
8. [BMJ Open: e096595](https://bmjopen.bmj.com/content/15/3/e096595)

## Meet the Team

This project was built collaboratively by Team SCREAM:
- **Adarsh Tripathi**
- **David Colín**
- **Jesper Boon**
- **Kevine Shima**
- **Luiscza**
- **Marcell Matei**
- **Yenus Ibrahim Ayalew**
