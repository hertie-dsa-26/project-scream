from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly, json
from app.utils.data import load_brfss

explorer_bp = Blueprint("explorer", __name__)


@explorer_bp.route("/")
def explorer():
    chart1 = None
    error = None

    try:
        df = load_brfss()

        depression_labels = {1: "Yes", 2: "No", 7: "Don't know", 9: "Refused"}
        counts = df["has_depression"].map(depression_labels).value_counts()
        pcts   = counts / counts.sum() * 100
        labels = counts.index.tolist()
        colors = ["#e74c3c", "#2ecc71", "#95a5a6", "#bdc3c7"]

        trace_counts = go.Bar(
            x=labels, y=counts.values.tolist(),
            marker_color=colors,
            text=[f"{v:,.0f}" for v in counts.values],
            textposition="outside", visible=True, name="Count",
        )
        trace_pcts = go.Bar(
            x=labels, y=[round(p, 1) for p in pcts.values],
            marker_color=colors,
            text=[f"{p:.1f}%" for p in pcts.values],
            textposition="outside", visible=False, name="Percentage",
        )

        updatemenus = [{
            "type": "buttons", "direction": "right", "x": 0.0, "y": 1.15,
            "buttons": [
                {"label": "Counts",      "method": "update",
                 "args": [{"visible": [True, False]}, {"yaxis": {"title": "Number of Respondents"}}]},
                {"label": "Percentages", "method": "update",
                 "args": [{"visible": [False, True]}, {"yaxis": {"title": "% of Respondents"}}]},
            ],
        }]

        fig = go.Figure(
            data=[trace_counts, trace_pcts],
            layout=go.Layout(
                title="(Ever told) you had a depressive disorder — BRFSS 2024",
                yaxis=dict(title="Number of Respondents"),
                xaxis=dict(title="Response"),
                updatemenus=updatemenus,
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=100),
            ),
        )
        chart1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        error = str(e)

    return render_template("explorer.html", chart1=chart1, error=error)
