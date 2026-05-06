[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# SCREAM: Diabetes Risk Predictor

SCREAM is an interactive web application that uses machine learning to estimate an individual\'s risk of developing diabetes based on behavioral, demographic, and health factors. Our predictive models are powered by the 2024 Behavioral Risk Factor Surveillance System (BRFSS) dataset from the CDC.

## Setup & Installation

**Prerequisites:** 
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (our chosen Python package manager)

**1. Clone the repository and install dependencies:**
\\ash
git clone https://github.com/hertie-dsa-26/project-scream.git
cd project-scream
uv sync
\
**2. Data Requirements:**
To train the model, run predictions, or view the Explorer, you must have the dataset subset locally.
* Place the \rfss2024_subset.parquet\ file inside \data/subsets/\.

**3. Generate Model Artifacts:**
Because the model artifacts are not stored in version control, you must generate them locally before starting the app:
\\ash
uv run python train_model.py
\*(This will generate \pipeline.joblib\, \metrics.json\, and \coefficients.json\ in \pp/model/artifacts/\)*

**4. Run the Flask App:**
Start the development server:
\\ash
uv run flask --app run.py run --debug
\The app will now be accessible at \http://127.0.0.1:5000/\.

**5. Running Tests (Optional):**
To execute the robust test suite (data models, validation factors), run:
\\ash
uv run pytest tests/ -v
\
## Features

- **Personalized Risk Prediction:** Users submit health factors via an intuitive UI to receive a tailored diabetes risk probability and categorization.
- **Actionable Health Suggestions:** Provides dynamic counterfactual recommendations (e.g., stopping smoking, improving physical activity) indicating exactly how lifestyle adjustments can lower the user\'s personal risk score.
- **Data Explorer:** An interactive dashboard exploring relationships between demographic/lifestyle factors and diabetes prevalence across the U.S.

## Data & Methodology

The model is trained on a ~400,000-response dataset from the **2024 BRFSS**, using approximately 75 variables filtering for demographics, general health, chronic conditions, lifestyle, and social determinants. We trained a **Support Vector Machine (SVM)** pipeline integrated tightly with a Flask backend.

**Download the raw dataset:**
- [Official CDC Website](https://www.cdc.gov/brfss/annual_data/annual_2024.html)
- [Google Drive Mirror](https://drive.google.com/file/d/1rp-CuzP-wnhk3gEbNib1MZ5ci_r8etMw/view?usp=sharing)

*(Note: Data dictionaries mapping BRFSS codebooks to pipeline features were utilized internally during the EDA phase.)*

## Architecture & Code Structure

The application follows a highly modular structure with clear separation of concerns:
- **\pp/routes/\**: Handles the web endpoints, rendering views, and coordinating application logic.
- **\pp/utils/\**: Core logic including robust input validation (\alidation.py\), model ingestion (\model.py\), and data processing.
- **\pp/model/artifacts/\**: Stores the locally generated machine learning pipeline models.
- **\	ests/\**: A robust Pytest suite combined with GitHub Actions CI ensuring quality check coverage against regressions, validations, and bounds limits.
- **\pipeline/\**: Contains scripts for sub-setting and processing raw BRFSS data.

## Meet the Team

This project was built collaboratively by Team SCREAM:
- **Adarsh Tripathi**
- **David Colín**
- **Jesper Boon**
- **Kevine Shima**
- **Luiscza**
- **Marcell Matei**
- **Yenus Ibrahim Ayalew**
