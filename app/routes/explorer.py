"""
Explorer blueprint  —  /explorer

Serves pre-aggregated chart data for the diabetes EDA page.

GET  /explorer          renders the page shell (chart containers only)
GET  /explorer/data     returns JSON with all chart data for Plotly
"""

from __future__ import annotations

import json

import pandas as pd
import plotly
import plotly.graph_objs as go
from flask import Blueprint, render_template, jsonify, session

from app.utils.data import load_brfss, _diabetes_binary

explorer_bp = Blueprint("explorer", __name__)

# ── Label maps ────────────────────────────────────────────────────────────────

_DIABETES_LABELS  = {0: "No diabetes", 1: "Diabetes"}
_SMOKING_LABELS   = {1.0: "Daily smoker", 2.0: "Some-days", 3.0: "Former", 4.0: "Never"}
_ACTIVITY_LABELS  = {1.0: "Active", 2.0: "Inactive"}
_ALCOHOL_LABELS   = {1.0: "Yes", 2.0: "No"}
_GENHEALTH_LABELS = {1.0: "Excellent", 2.0: "Very good", 3.0: "Good", 4.0: "Fair", 5.0: "Poor"}
_INCOME_LABELS    = {
    1.0: "< $15k", 2.0: "$15–25k", 3.0: "$25–35k", 4.0: "$35–50k",
    5.0: "$50–100k", 6.0: "$100–150k", 7.0: "$150–200k", 8.0: "> $200k",
}

_COLORS = {
    "no_diabetes": "#60a5fa",   # blue
    "diabetes":    "#f87171",   # red
    "neutral":     ["#60a5fa", "#34d399", "#818cf8", "#f87171", "#a78bfa",
                    "#fb923c", "#4ade80", "#38bdf8"],
}

_PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", size=12),
    margin=dict(l=40, r=20, t=60, b=40),
)


# ── Chart builders ────────────────────────────────────────────────────────────

def _chart_outcome_distribution(df: pd.DataFrame) -> str:
    """Chart 1: Overall diabetes outcome distribution with count/% toggle."""
    counts = _diabetes_binary(df).map(_DIABETES_LABELS).value_counts()
    pcts   = counts / counts.sum() * 100
    labels = counts.index.tolist()
    colors = [_COLORS["diabetes"] if l == "Diabetes" else _COLORS["no_diabetes"] for l in labels]

    fig = go.Figure(data=[
        go.Bar(
            name="Count", x=labels, y=counts.values.tolist(),
            marker_color=colors,
            text=[f"{v:,.0f}" for v in counts.values],
            textposition="outside", visible=True,
        ),
        go.Bar(
            name="Percentage", x=labels, y=[round(p, 1) for p in pcts.values],
            marker_color=colors,
            text=[f"{p:.1f}%" for p in pcts.values],
            textposition="outside", visible=False,
        ),
    ])
    fig.update_layout(
        **_PLOTLY_BASE,
        title="Diabetes prevalence — BRFSS 2024",
        showlegend=False,
        yaxis=dict(title="Respondents", showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                   range=[0, max(counts.values.tolist()) * 1.15]),
        xaxis=dict(title=""),
        updatemenus=[{
            "type": "buttons", "direction": "right",
            "x": 1.0, "xanchor": "right", "y": 1.0, "yanchor": "top",
            "buttons": [
                {"label": "Count", "method": "update",
                 "args": [{"visible": [True, False]},
                           {"yaxis": {"title": "Respondents",
                                       "range": [0, max(counts.values.tolist()) * 1.15],
                                       "showgrid": True, "gridcolor": "rgba(0,0,0,0.06)"}}]},
                {"label": "Percentage", "method": "update",
                 "args": [{"visible": [False, True]},
                           {"yaxis": {"title": "% of respondents",
                                       "range": [0, max([round(p, 1) for p in pcts.values]) * 1.15],
                                       "showgrid": True, "gridcolor": "rgba(0,0,0,0.06)"}}]},
            ],
        }],
    )
    return _to_json(fig)


def _chart_age_by_diabetes(df: pd.DataFrame, user_age: float | None = None) -> str:
    """Chart 2: Age distribution split by diabetes status."""
    combined = pd.DataFrame({
        "age":      df["age_imputed"].values,
        "diabetes": _diabetes_binary(df).values,
    }).dropna()

    diabetic     = combined.loc[combined["diabetes"] == 1, "age"].tolist()
    non_diabetic = combined.loc[combined["diabetes"] == 0, "age"].tolist()

    fig = go.Figure(data=[
        go.Histogram(
            name="No diabetes", x=non_diabetic, nbinsx=30,
            marker_color=_COLORS["no_diabetes"], opacity=0.75,
        ),
        go.Histogram(
            name="Diabetes", x=diabetic, nbinsx=30,
            marker_color=_COLORS["diabetes"], opacity=0.75,
        ),
    ])
    if user_age is not None:
        fig.add_vline(
            x=user_age, line_width=2, line_dash="dash", line_color="#f59e0b",
            annotation_text=f"You ({int(user_age)})",
            annotation_position="top right",
            annotation_font_color="#f59e0b",
        )

    fig.update_layout(
        **_PLOTLY_BASE,
        title="Age distribution by diabetes status",
        barmode="overlay",
        yaxis=dict(title="Respondents", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        xaxis=dict(title="Age"),
        legend=dict(orientation="h", y=1.12),
    )
    return _to_json(fig)


def _chart_lifestyle_vs_diabetes(df: pd.DataFrame, user: dict | None = None) -> str:
    """Chart 3: Lifestyle factors (activity, smoking, alcohol) vs diabetes — grouped bars."""
    diabetes = _diabetes_binary(df)
    valid    = diabetes.notna()
    target   = diabetes[valid]
    df       = df[valid]

    def _pct_diabetic(series: pd.Series, label_map: dict) -> tuple[list, list]:
        results = {}
        for code, label in label_map.items():
            mask  = series == code
            total = mask.sum()
            if total == 0:
                continue
            pct = (target[mask] == 1).sum() / total * 100
            results[label] = round(pct, 1)
        return list(results.keys()), list(results.values())

    act_labels, act_vals  = _pct_diabetic(df["any_physical_activity"], _ACTIVITY_LABELS)
    smk_labels, smk_vals  = _pct_diabetic(df["smoking_status"],        _SMOKING_LABELS)
    alc_labels, alc_vals  = _pct_diabetic(df["any_alcohol_past_30d"],  _ALCOHOL_LABELS)

    # Build per-bar colors, highlighting the user's category in amber
    def _bar_colors(labels, user_val, label_map, base_color):
        user_label = label_map.get(user_val) if user_val is not None else None
        return ["#f59e0b" if l == user_label else base_color for l in labels]

    act_colors = _bar_colors(act_labels, user.get("activity") if user else None, _ACTIVITY_LABELS, _COLORS["neutral"][0])
    smk_colors = _bar_colors(smk_labels, user.get("smoking")  if user else None, _SMOKING_LABELS,  _COLORS["neutral"][1])
    alc_colors = _bar_colors(alc_labels, user.get("alcohol")  if user else None, _ALCOHOL_LABELS,  _COLORS["neutral"][2])

    def _user_label(user_val, label_map):
        """Return the label string for the user's category, or None."""
        return label_map.get(user_val) if user_val is not None else None

    user_act_label = _user_label(user.get("activity") if user else None, _ACTIVITY_LABELS)
    user_smk_label = _user_label(user.get("smoking")  if user else None, _SMOKING_LABELS)
    user_alc_label = _user_label(user.get("alcohol")  if user else None, _ALCOHOL_LABELS)

    def _bar_text(labels, user_label, vals):
        """Return text annotations — 'You' above user bar, blank elsewhere."""
        return ["You" if l == user_label else "" for l in labels]

    fig = go.Figure(data=[
        go.Bar(name="Physical activity", x=act_labels, y=act_vals,
               marker_color=act_colors, visible=True,
               text=_bar_text(act_labels, user_act_label, act_vals),
               textposition="outside", textfont=dict(color="#f59e0b", size=11)),
        go.Bar(name="Smoking status",    x=smk_labels, y=smk_vals,
               marker_color=smk_colors, visible=False,
               text=_bar_text(smk_labels, user_smk_label, smk_vals),
               textposition="outside", textfont=dict(color="#f59e0b", size=11)),
        go.Bar(name="Alcohol use",       x=alc_labels, y=alc_vals,
               marker_color=alc_colors, visible=False,
               text=_bar_text(alc_labels, user_alc_label, alc_vals),
               textposition="outside", textfont=dict(color="#f59e0b", size=11)),
    ])

    n_act, n_smk, n_alc = len(act_labels), len(smk_labels), len(alc_labels)

    fig.update_layout(
        **_PLOTLY_BASE,
        title="% diabetic by lifestyle factor",
        showlegend=False,
        yaxis=dict(title="% diabetic", showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                   range=[0, 30]),
        xaxis=dict(title=""),
        updatemenus=[{
            "type": "buttons", "direction": "right", "x": 1.0, "xanchor": "right", "y": 1.0, "yanchor": "top",
            "buttons": [
                {"label": "Physical activity", "method": "update",
                 "args": [{"visible": [True, False, False]},
                          {"title": "% diabetic by physical activity"}]},
                {"label": "Smoking status", "method": "update",
                 "args": [{"visible": [False, True, False]},
                          {"title": "% diabetic by smoking status"}]},
                {"label": "Alcohol use", "method": "update",
                 "args": [{"visible": [False, False, True]},
                          {"title": "% diabetic by alcohol use (past 30 days)"}]},
            ],
        }],
    )
    return _to_json(fig)


def _chart_bmi_by_diabetes(df: pd.DataFrame, user_bmi: float | None = None) -> str:
    """Chart 4: BMI distribution by diabetes status (using bmi_x100 / 100)."""
    combined = pd.DataFrame({
        "bmi":      (df["bmi_x100"] / 100).values,
        "diabetes": _diabetes_binary(df).values,
    }).dropna()

    diabetic     = combined.loc[combined["diabetes"] == 1, "bmi"].tolist()
    non_diabetic = combined.loc[combined["diabetes"] == 0, "bmi"].tolist()

    fig = go.Figure(data=[
        go.Histogram(
            name="No diabetes", x=non_diabetic, nbinsx=40,
            marker_color=_COLORS["no_diabetes"], opacity=0.75,
        ),
        go.Histogram(
            name="Diabetes", x=diabetic, nbinsx=40,
            marker_color=_COLORS["diabetes"], opacity=0.75,
        ),
    ])
    if user_bmi is not None:
        fig.add_vline(
            x=user_bmi, line_width=2, line_dash="dash", line_color="#f59e0b",
            annotation_text=f"You ({user_bmi:.1f})",
            annotation_position="top right",
            annotation_font_color="#f59e0b",
        )

    fig.update_layout(
        **_PLOTLY_BASE,
        title="BMI distribution by diabetes status",
        barmode="overlay",
        yaxis=dict(title="Respondents", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        xaxis=dict(title="BMI", range=[10, 70]),
        legend=dict(orientation="h", y=1.12),
    )
    return _to_json(fig)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _toggle_menu(labels: list[str], y_titles: list[str]) -> dict:
    """Standard count/percentage toggle button menu."""
    return {
        "type": "buttons", "direction": "right", "x": 1.0, "xanchor": "right", "y": 1.0, "yanchor": "top",
        "buttons": [
            {
                "label": label,
                "method": "update",
                "args": [
                    {"visible": [i == idx for i in range(len(labels))]},
                    {"yaxis": {"title": y_titles[idx],
                               "showgrid": True,
                               "gridcolor": "rgba(0,0,0,0.06)"}},
                ],
            }
            for idx, label in enumerate(labels)
        ],
    }


def _to_json(fig) -> str:
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


# ── Routes ────────────────────────────────────────────────────────────────────

@explorer_bp.route("/")
def explorer():
    return render_template("explorer.html")


@explorer_bp.route("/data")
def explorer_data():
    """Return all chart JSON for the frontend to render."""
    try:
        df = load_brfss()

        # Extract user values from session for highlight overlays.
        # session["last_form_values"] = dict(request.form) which stores plain strings.
        fv = session.get("last_form_values", {})

        def _fv(key):
            """Safely get a scalar value from the form dict (always plain strings)."""
            val = fv.get(key)
            if val is None:
                return None
            # Handle both plain string and legacy list format
            if isinstance(val, list):
                val = val[0] if val else None
            return val

        user_age = float(_fv("age")) if _fv("age") else None
        user_bmi = None
        if _fv("height_cm") and _fv("weight_kg"):
            try:
                h = float(_fv("height_cm")) / 100
                w = float(_fv("weight_kg"))
                user_bmi = w / (h ** 2)
            except (ValueError, ZeroDivisionError):
                pass
        user_activity = float(_fv("any_physical_activity")) if _fv("any_physical_activity") else None
        user_smoking  = float(_fv("smoking_status")) if _fv("smoking_status") else None
        user_alcohol  = float(_fv("any_alcohol_past_30d")) if _fv("any_alcohol_past_30d") else None

        user = {
            "age":      user_age,
            "bmi":      user_bmi,
            "activity": user_activity,
            "smoking":  user_smoking,
            "alcohol":  user_alcohol,
        }

        return jsonify({
            "chart1": _chart_outcome_distribution(df),
            "chart2": _chart_age_by_diabetes(df, user_age=user["age"]),
            "chart3": _chart_lifestyle_vs_diabetes(df, user=user),
            "chart4": _chart_bmi_by_diabetes(df, user_bmi=user["bmi"]),
            "has_user_data": any(v is not None for v in user.values()),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500