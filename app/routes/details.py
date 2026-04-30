from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly, json
from app.utils.model import get_metrics, get_coefficients

details_bp = Blueprint("details", __name__)


@details_bp.route("/")
def index():
    try:
        metrics = get_metrics()
        coefficients = get_coefficients()
    except RuntimeError as e:
        return render_template("details/index.html", error=str(e))

    sig = [c for c in coefficients if c["p_value"] < 0.05]
    sig_sorted = sorted(sig, key=lambda x: x["odds_ratio"])

    features = [c["feature"] for c in sig_sorted]
    ors      = [c["odds_ratio"] for c in sig_sorted]
    colors   = ["#e74c3c" if o > 1 else "#2563eb" for o in ors]

    fig = go.Figure(go.Bar(
        x=ors, y=features, orientation="h",
        marker_color=colors,
        text=[f"{o:.2f}" for o in ors],
        textposition="outside",
    ))
    fig.add_vline(x=1.0, line_dash="dash", line_color="#888", line_width=1)
    fig.update_layout(
        title="Odds Ratios — significant predictors (p < 0.05)",
        xaxis_title="Odds Ratio  (> 1 increases risk, < 1 reduces risk)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans"),
        margin=dict(l=220, r=80, t=60, b=40),
        height=max(400, len(sig_sorted) * 26),
    )
    chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "details/index.html",
        metrics=metrics,
        coefficients=coefficients,
        chart_json=chart_json,
        error=None,
    )
