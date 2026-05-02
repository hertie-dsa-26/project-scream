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
from flask import Blueprint, render_template, jsonify

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
    "neutral":     ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa",
                    "#fb923c", "#4ade80", "#38bdf8"],
}

_PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
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
        yaxis=dict(title="Respondents", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        xaxis=dict(title=""),
        updatemenus=[_toggle_menu(["Count", "Percentage"],
                                  ["Respondents", "% of respondents"])],
    )
    return _to_json(fig)


def _chart_age_by_diabetes(df: pd.DataFrame) -> str:
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
    fig.update_layout(
        **_PLOTLY_BASE,
        title="Age distribution by diabetes status",
        barmode="overlay",
        yaxis=dict(title="Respondents", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        xaxis=dict(title="Age"),
        legend=dict(orientation="h", y=1.12),
    )
    return _to_json(fig)


def _chart_lifestyle_vs_diabetes(df: pd.DataFrame) -> str:
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

    fig = go.Figure(data=[
        go.Bar(name="Physical activity", x=act_labels, y=act_vals,
               marker_color=_COLORS["neutral"][0], visible=True),
        go.Bar(name="Smoking status",    x=smk_labels, y=smk_vals,
               marker_color=_COLORS["neutral"][1], visible=False),
        go.Bar(name="Alcohol use",       x=alc_labels, y=alc_vals,
               marker_color=_COLORS["neutral"][2], visible=False),
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
            "type": "buttons", "direction": "right", "x": 0.0, "y": 1.18,
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


def _chart_bmi_by_diabetes(df: pd.DataFrame) -> str:
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
        "type": "buttons", "direction": "right", "x": 0.0, "y": 1.15,
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
        return jsonify({
            "chart1": _chart_outcome_distribution(df),
            "chart2": _chart_age_by_diabetes(df),
            "chart3": _chart_lifestyle_vs_diabetes(df),
            "chart4": _chart_bmi_by_diabetes(df),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500