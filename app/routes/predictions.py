"""
Predictions blueprint  —  /predictions

GET  /predictions       render the empty form
POST /predictions       validate input, run model, render result
                        also stores result in session for /details
"""

from flask import Blueprint, render_template, request, session

from app.utils.validation import validate_prediction_input
from app.utils.model import predict

predictions_bp = Blueprint("predictions", __name__)

# Form option labels — kept here because they are purely presentation data
# for this route's template.
FORM_OPTIONS = {
    "sex": [
        (1, "Male"),
        (2, "Female"),
    ],
    "general_health": [
        (1, "Excellent"),
        (2, "Very good"),
        (3, "Good"),
        (4, "Fair"),
        (5, "Poor"),
    ],
    "education_level": [
        (1, "Never attended school or only kindergarten"),
        (2, "Grades 1–8 (elementary)"),
        (3, "Grades 9–11 (some high school)"),
        (4, "Grade 12 / GED or higher"),
    ],
    "income_level": [
        (1, "< $15k"),
        (2, "$15–25k"),
        (3, "$25–35k"),
        (4, "$35–50k"),
        (5, "$50–100k"),
        (6, "$100–150k"),
        (7, "> $150k"),
    ],
    "smoking_status": [
        (1, "Current smoker (daily)"),
        (2, "Current smoker (some days)"),
        (3, "Former smoker"),
        (4, "Never smoked"),
    ],
    "any_physical_activity": [
        (1, "Yes"),
        (2, "No"),
    ],
    "any_alcohol_past_30d": [
        (1, "Yes"),
        (2, "No"),
    ],
}

# Human-readable labels for fields whose auto-formatted key names are unclear.
# predictions.html uses this instead of the default key -> title formatting.
FORM_LABELS = {
    "sex":                   "Sex",
    "general_health":        "General health",
    "education_level":       "Education level",
    "income_level":          "Income level",
    "smoking_status":        "Smoking status",
    "any_physical_activity": "Any physical activity in the past month?",
    "any_alcohol_past_30d":  "Any alcohol in the past 30 days?",
}

# Tooltip text shown next to the label for fields that need extra explanation.
FORM_TOOLTIPS = {
    "general_health": (
        "Rate your overall health: Excellent means no limitations or health issues; "
        "Very good means minor issues; Good means some ongoing conditions; "
        "Fair means significant health problems affecting daily life; "
        "Poor means severe or disabling health conditions."
    ),
    "education_level": (
        "Select the highest level of education you have completed. "
        "Grade 12 / GED or higher includes any college or postgraduate education."
    ),
    "income_level": (
        "Select your total annual household income before taxes, "
        "including all sources for everyone living in your home."
    ),
    "any_physical_activity": (
        "Any leisure-time physical activity counts — walking, sports, gym, gardening, "
        "or any other exercise done in the past 30 days outside of your regular job."
    ),
    "any_alcohol_past_30d": (
        "Any drink counts — beer, wine, spirits, or any other alcoholic beverage "
        "consumed at least once in the past 30 days."
    ),
}


@predictions_bp.route("/", methods=["GET", "POST"])
def predictions():
    result      = None
    form_errors = {}

    if request.method == "POST":
        cleaned, form_errors = validate_prediction_input(request.form)

        if not form_errors:
            result = predict(cleaned)

            # Store in session so /details can access without re-running model
            session["last_result"] = {
                "probability_pct": result.probability_pct,
                "risk_category":   result.risk_category,
                "suggestions":     result.suggestions,
                "input_features":  result.input_features,
            }

    return render_template(
        "predictions.html",
        form_options   = FORM_OPTIONS,
        form_labels    = FORM_LABELS,
        form_tooltips  = FORM_TOOLTIPS,
        form_values    = request.form,
        form_errors    = form_errors,
        result         = result,
    )