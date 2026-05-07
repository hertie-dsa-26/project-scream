"""
Home blueprint  —  / and /home

Landing page only: choropleth map + CTA button to /predictions.
No form, no model calls here.
"""

from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly
import json

home_bp = Blueprint("home", __name__)

# US state abbreviations for the choropleth
_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
]

# ---------------------------------------------------------------------------
# BRFSS 2024 state-level diabetes prevalence (% of adults, age-adjusted).
# Source: CDC BRFSS 2024 Prevalence & Trends Data.
# TODO: replace with values computed from the loaded dataset in utils/data.py
#       once the data layer is wired up in Phase 3.
# ---------------------------------------------------------------------------
_PREVALENCE = {
    "AL": 13.9, "AK": 8.1,  "AZ": 10.6, "AR": 13.4, "CA": 9.8,
    "CO": 7.6,  "CT": 9.0,  "DE": 11.0, "FL": 11.2, "GA": 12.3,
    "HI": 10.3, "ID": 8.9,  "IL": 10.1, "IN": 12.0, "IA": 8.6,
    "KS": 10.2, "KY": 13.5, "LA": 13.8, "ME": 9.5,  "MD": 10.2,
    "MA": 8.4,  "MI": 11.2, "MN": 7.8,  "MS": 15.2, "MO": 11.6,
    "MT": 8.2,  "NE": 9.1,  "NV": 10.5, "NH": 8.3,  "NJ": 9.8,
    "NM": 11.0, "NY": 10.0, "NC": 11.5, "ND": 8.5,  "OH": 11.8,
    "OK": 13.2, "OR": 8.7,  "PA": 10.9, "RI": 9.6,  "SC": 13.0,
    "SD": 9.3,  "TN": 13.7, "TX": 11.8, "UT": 7.9,  "VT": 7.5,
    "VA": 10.0, "WA": 8.5,  "WV": 15.0, "WI": 8.9,  "WY": 8.6,
    "DC": 9.2,
}


def _build_map() -> str:
    z_values   = [_PREVALENCE.get(s, 0) for s in _STATES]
    hover_text = [
        f"<b>{s}</b><br>{_PREVALENCE.get(s, 'N/A')}% diabetic"
        for s in _STATES
    ]

    fig = go.Figure(go.Choropleth(
        locations       = _STATES,
        z               = z_values,
        text            = hover_text,
        hoverinfo       = "text",
        locationmode    = "USA-states",
        colorscale      = "Blues",
        zmin            = 5,
        zmax            = 16,
        colorbar_title  = "% diabetic",
        marker_line_color = "white",
        marker_line_width = 0.5,
    ))
    fig.update_layout(
        title_text       = "Diabetes prevalence by state — BRFSS 2024",
        geo_scope        = "usa",
        paper_bgcolor    = "rgba(0,0,0,0)",
        plot_bgcolor     = "rgba(0,0,0,0)",
        margin           = dict(l=0, r=0, t=40, b=0),
        font             = dict(family="DM Sans"),
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@home_bp.route("/", methods=["GET"])
@home_bp.route("/home", methods=["GET"])
def home():
    return render_template(
        "home.html",
        map_json = _build_map(),
    )