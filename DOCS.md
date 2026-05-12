# SCREAM — App Documentation

SCREAM is a Flask web app that lets users estimate their personal diabetes risk based on BRFSS 2024 survey data. Users fill in a short health questionnaire, receive a risk category (low / moderate / high), and can explore what factors drive the estimate and how lifestyle changes might affect it.

---

## Running the app locally

### Prerequisites
- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv) for dependency management
- The BRFSS parquet at `data/subsets/brfss2024_subset.parquet` (see README for download links)

### Steps

```bash
# Install dependencies
uv sync

# Run the app
uv run flask --app run.py run
```

The app will be available at `http://127.0.0.1:5000`.

---

## Running the tests

```bash
uv run pytest tests/ -v
```

Tests in `tests/test_data.py` that require the BRFSS parquet are skipped automatically if the file is not present. All other tests run without it.

---

## Retraining the model

If you need to regenerate the SVM artifacts (e.g. after a sklearn version change):

```bash
uv run python retrain_svm.py
```

This retrains the ManualSVM on `literature/diabetes_risk_literature_subset.csv` and writes fresh `svm_model.pkl`, `scaler.pkl`, and `feature_columns.json` to `app/model/artifacts/`. Expected output: accuracy ~0.71, recall ~0.71, ROC-AUC ~0.78.

**Important:** the script imports `ManualSVM` from `app.utils.model` so that joblib serialises the class under the correct module path. Do not move the class definition or the saved pickle will fail to load.

---

## Project structure

```
project-scream/
├── app/                        # Flask application
│   ├── __init__.py             # App factory — registers blueprints, loads model at startup
│   ├── model/
│   │   └── artifacts/          # Trained model files
│   │       ├── svm_model.pkl   # ManualSVM instance (retrained with sklearn 1.8.0)
│   │       ├── scaler.pkl      # StandardScaler fitted on training features
│   │       └── feature_columns.json  # Ordered list of 9 input features
│   ├── references.json         # Citation objects for all features, rendered on details page
│   ├── routes/
│   │   ├── home.py             # Landing page — choropleth map + CTA
│   │   ├── predictions.py      # Prediction form + result
│   │   ├── explorer.py         # EDA charts (serves /explorer/data as JSON)
│   │   └── details.py          # Personalised breakdown of last prediction
│   ├── static/
│   │   └── css/
│   │       ├── main.css        # All reusable component styles
│   │       └── story.css       # Scrollytelling layout (home page only)
│   ├── templates/
│   │   ├── layout.html         # Base layout (sidebar nav)
│   │   ├── layout_story.html   # Base layout (sticky header, full-width)
│   │   ├── home.html           # Scrollytelling landing page
│   │   ├── predictions.html    # Prediction form + result
│   │   ├── explorer.html       # EDA chart page
│   │   └── details/
│   │       └── index.html      # Personalised result breakdown
│   └── utils/
│       ├── data.py             # Data loading, caching, benchmark computation
│       ├── model.py            # ManualSVM class, loading, prediction, scoring
│       └── validation.py       # Input validation — called by predictions route
├── data/
│   ├── raw/                    # Raw BRFSS XPT file (not committed)
│   └── subsets/
│       └── brfss2024_subset.parquet  # Processed subset used by the app (not committed)
├── eda/                        # Exploratory notebooks (not used by app directly)
├── literature/
│   ├── diabetes_risk_literature_subset.csv  # Training data for ManualSVM
│   ├── diabetes_risk_data_preparation.md    # Documents data prep decisions
│   └── diabetes_risk_literature_synthesis.md  # Literature review summary
├── pipeline/                   # Data preparation and model training (separate from app)
│   ├── Subsetting.py           # Creates the BRFSS subset parquet
│   ├── New_subset_without_NaN.py
│   └── Adarsh_SVM_pipline.ipynb  # Original SVM training notebook
├── tests/                      # App test suite
│   ├── test_validation.py      # Input validation tests (36 tests)
│   ├── test_model.py           # Model prediction tests (20 tests)
│   └── test_data.py            # Data layer tests (19 tests, parquet-dependent skipped on CI)
├── conftest.py                 # Adds project root to sys.path for pytest
├── retrain_svm.py              # Retrains and saves SVM artifacts
├── config.py                   # Flask config (DATA_DIR, SECRET_KEY, etc.)
├── run.py                      # App entrypoint
└── .github/
    └── workflows/
        └── test.yml            # CI — runs pytest on push/PR to main
```

---

## Architecture

The app follows a strict three-layer separation:

```
routes/       HTTP only — parse request, call utils, render template
utils/        Business logic — model inference, data aggregation, validation
model/        Artifacts only — no Python logic lives here
```

**The key rule:** routes never touch numpy, sklearn, or raw data directly. Everything goes through `utils/`.

### Request flow for a prediction

1. User submits the form → `routes/predictions.py`
2. Route calls `utils/validation.validate_prediction_input(form_data)` → returns cleaned dict or field-level errors
3. Height and weight are converted to BMI under the hood; the form never exposes raw BMI
4. If valid, route calls `utils/model.predict(cleaned)` → returns a `PredictResult` dataclass
5. Result is stored in Flask session so `/details` can access it without re-running the model
6. Form values are also stored in session so they repopulate on back-navigation

### Model — ManualSVM

The classifier is a from-scratch linear SVM (`ManualSVM` in `utils/model.py`), trained with SGD and hinge loss. It satisfies the course requirement for a custom algorithm implementation.

**Why ManualSVM rather than sklearn SVM:** the rubric requires a from-scratch implementation that the team can explain, including its complexity and limitations.

**Risk scoring:** the ManualSVM only produces hard 0/1 predictions. For continuous risk scoring, we apply a sigmoid to the raw decision value (`np.dot(X, w) - b`), giving a monotone 0–1 score. This is the standard approximation for linear SVMs without `predict_proba`. The score is displayed as a percentage but is **not a calibrated probability** — the UI labels it as an "estimated risk score".

**Risk thresholds:** low < 40%, moderate 40–60%, high > 60%. These were chosen so that the ~15% population prevalence maps to sensible category distributions.

**Counterfactuals:** for actionable suggestions (physical activity, smoking), we rerun scoring with the feature set to its "best" value and report the delta. The quit-smoking suggestion always appears for current smokers regardless of delta size, because the evidence base is stronger than the model's effect estimate.

### Model loading

The SVM, scaler, and feature columns are loaded once at startup via `load_model()` in `app/__init__.py`. This avoids cold-load latency on the first request.

### Global template variables

The medical disclaimer is injected into every template automatically via a `context_processor` in `app/__init__.py`. Routes never need to pass it explicitly.

### Input validation

`utils/validation.py` enforces:
- Age: 18–99
- Height: 100–250 cm (converted from ft+in if imperial)
- Weight: 30–300 kg (converted from lbs if imperial)
- Computed BMI sanity check: 10–70
- Categorical codes must match what the pipeline was trained on exactly: `income_level` 1–7, `education_level` 1–4

---

## Pages

| Route | Purpose |
|---|---|
| `/` | Scrollytelling landing page — choropleth map, southern belt zoom, CTAs |
| `/predictions` | Prediction form + result with counterfactual suggestions |
| `/explorer` | Interactive EDA charts from BRFSS data |
| `/explorer/data` | JSON endpoint serving chart data to the frontend |
| `/details` | Personalised breakdown — population benchmarks, SVM weights, citations |

---

## Key files to know

| File | What to edit here |
|---|---|
| `app/utils/validation.py` | Valid input ranges and category codes — must match pipeline's known categories |
| `app/utils/model.py` | ManualSVM class, risk thresholds, actionable features, counterfactual logic |
| `app/utils/data.py` | Data loading path, benchmark features, display labels, state prevalence |
| `app/routes/predictions.py` | Form option labels, tooltips, form persistence logic |
| `app/references.json` | Citations — add/update author, year, url per feature |
| `retrain_svm.py` | Re-run this if sklearn version changes or training data is updated |
| `config.py` | `DATA_DIR` path and Flask secret key |

---

## Notes for graders

- The pipeline folder is independent of the app — it contains data subsetting and the original SVM training notebook. The app only consumes the trained artifacts in `app/model/artifacts/`.
- The BRFSS parquet is not committed (too large). Download it via the links in the README and place it at `data/subsets/brfss2024_subset.parquet`. The app will fail to load the home page map and explorer charts without it, but predictions will still work since those use the smaller `literature/diabetes_risk_literature_subset.csv` indirectly via the trained artifacts.
- The ManualSVM is implemented from scratch in `app/utils/model.py`. The class definition must live there (not in `retrain_svm.py`) so that joblib can deserialise the saved pickle correctly when the app loads.
- Input validation is strict because the StandardScaler and SVM were trained on a specific feature set. Submitting out-of-range or unknown values would produce silently wrong predictions rather than errors, so the validator catches them before they reach the model.
- Tennessee (FIPS 47) is absent from the BRFSS subset used by this project and appears as a gap on the home page map. This is a data collection issue, not a bug.

#### Additionally on code quality:

This project followed a clean and disciplined Git workflow:

- All work was done on feature branches, never directly on main.
- Every Pull Request was reviewed by at least one other team member before merging.
- The main branch remained protected and stable at all times.
- Workflow and coding standards followed the repo’s [Contributing Guidelines](Contributing_Regulations.md), ensuring consistent GitHub hygiene and collaborative best practices.

