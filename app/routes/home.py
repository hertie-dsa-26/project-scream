from flask import Blueprint, render_template, request
import plotly.graph_objs as go
import plotly, json
import pandas as pd
from app.utils.model import get_pipeline, get_metrics

home_bp = Blueprint("home", __name__)

_STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
]

FORM_OPTIONS = {
    "sex":                  [(1, "Male"), (2, "Female")],
    "general_health":       [(1, "Excellent"), (2, "Very good"), (3, "Good"), (4, "Fair"), (5, "Poor")],
    "education_level":      [(1, "Never attended school"), (2, "Grades 1–8"), (3, "Grades 9–11"),
                             (4, "Grade 12 / GED"), (5, "Some college"), (6, "College graduate")],
    "income_level":         [(1, "< $15k"), (2, "$15–25k"), (3, "$25–35k"), (4, "$35–50k"),
                             (5, "$50–100k"), (6, "$100–150k"), (7, "$150–200k"), (8, "> $200k")],
    "smoking_status":       [(1, "Current smoker (daily)"), (2, "Current smoker (some days)"),
                             (3, "Former smoker"), (4, "Never smoked")],
    "any_physical_activity": [(1, "Yes"), (2, "No")],
    "any_alcohol_past_30d":  [(1, "Yes"), (2, "No")],
}

# Features the patient can actually change — used for the wake-up call
_ACTIONABLE = [
    {
        "key":       "any_physical_activity",
        "label":     "Get physically active",
        "tip":       "People who exercise at least occasionally have a significantly lower estimated diabetes risk.",
        "best":      1.0,
        "active_if": lambda v: v == 2.0,
    },
    {
        "key":       "smoking_status",
        "label":     "Quit smoking",
        "tip":       "Quitting smoking improves metabolic health and reduces long-term diabetes risk.",
        "best":      4.0,
        "active_if": lambda v: v in (1.0, 2.0),
    },
]

_DIET_TIP = {
    "label": "Improve your diet",
    "tip":   "Reducing sugar, processed foods, and refined carbs is one of the strongest evidence-based ways to prevent diabetes — an effect our model does not directly capture.",
    "static": True,
}


def _build_map() -> str:
    fig = go.Figure(go.Choropleth(
        locations=_STATES,
        z=[0] * len(_STATES),
        locationmode="USA-states",
        colorscale="Blues",
        zmin=0, zmax=20,
        colorbar_title="% diabetic",
        marker_line_color="white",
        marker_line_width=0.5,
    ))
    fig.update_layout(
        title_text="Diabetes prevalence by state — BRFSS 2024",
        geo_scope="usa",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        font=dict(family="DM Sans"),
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@home_bp.route("/", methods=["GET", "POST"])
@home_bp.route("/home", methods=["GET", "POST"])
def home():
    result = None
    risk_level = None
    suggestions = []
    error = None

    if request.method == "POST":
        try:
            medians = get_metrics()["numeric_medians"]
            inputs = {
                "age_imputed":          float(request.form["age"]),
                "bmi_x100":             float(request.form["bmi"]) * 100,
                "height_inches":        medians["height_inches"],
                "weight_kg":            medians["weight_kg"],
                "sex":                  float(request.form["sex"]),
                "general_health":       float(request.form["general_health"]),
                "education_level":      float(request.form["education_level"]),
                "income_level":         float(request.form["income_level"]),
                "smoking_status":       float(request.form["smoking_status"]),
                "any_physical_activity": float(request.form["any_physical_activity"]),
                "any_alcohol_past_30d": float(request.form["any_alcohol_past_30d"]),
            }

            pipeline = get_pipeline()
            base_prob = pipeline.predict_proba(pd.DataFrame([inputs]))[0, 1] * 100
            result = round(base_prob, 1)

            if result < 10:
                risk_level = "low"
            elif result < 25:
                risk_level = "moderate"
            else:
                risk_level = "high"

            for action in _ACTIONABLE:
                val = inputs[action["key"]]
                if action["active_if"](val):
                    modified = {**inputs, action["key"]: action["best"]}
                    new_prob = pipeline.predict_proba(pd.DataFrame([modified]))[0, 1] * 100
                    delta = base_prob - new_prob
                    if delta > 0.5:
                        suggestions.append({
                            "label":    action["label"],
                            "tip":      action["tip"],
                            "new_prob": round(new_prob, 1),
                            "delta":    round(delta, 1),
                        })

            suggestions.append(_DIET_TIP)

        except RuntimeError as e:
            error = str(e)
        except Exception as e:
            error = f"Could not compute prediction: {e}"

    return render_template(
        "home.html",
        map_json=_build_map(),
        form_options=FORM_OPTIONS,
        form_values=request.form,
        result=result,
        risk_level=risk_level,
        suggestions=suggestions,
        error=error,
    )
