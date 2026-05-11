"""
Home blueprint  —  / and /home

Landing page only: choropleth map + CTA button to /predictions.
No form, no model calls here.
"""

from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly
import json

from app.utils.data import get_state_prevalence

home_bp = Blueprint("home", __name__)

# US state abbreviations for the choropleth
_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
]

def _build_map() -> str:
    prevalence = get_state_prevalence()

    # For any state missing from the dataset, use 0 as a sentinel
    # so it renders visibly different rather than silently wrong
    z_values   = [prevalence.get(s, 0) for s in _STATES]
    hover_text = [
        f"<b>{s}</b><br>{prevalence.get(s, 'N/A')}% diabetic"
        for s in _STATES
    ]

    # Set color scale using 5th-95th percentile to avoid outlier stretch
    valid_z = sorted([z for z in z_values if z > 0])
    if valid_z:
        n = len(valid_z)
        p5  = valid_z[max(0, int(n * 0.05))]
        p95 = valid_z[min(n - 1, int(n * 0.95))]
        zmin = round(p5  - 0.5, 1)
        zmax = round(p95 + 0.5, 1)
    else:
        zmin, zmax = 5, 20

    fig = go.Figure(go.Choropleth(
        locations       = _STATES,
        z               = z_values,
        text            = hover_text,
        hoverinfo       = "text",
        locationmode    = "USA-states",
        colorscale      = "Blues",
        zmin            = zmin,
        zmax            = zmax,
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
        map_json    = _build_map(),
        states_json = json.dumps(_STATES),
    )