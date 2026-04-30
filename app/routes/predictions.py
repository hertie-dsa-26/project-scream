from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly, json

predictions_bp = Blueprint("predictions", __name__)

_STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
]


@predictions_bp.route("/")
def predictions():
    fig = go.Figure(go.Choropleth(
        locations=_STATES,
        z=[0] * len(_STATES),
        locationmode="USA-states",
        colorscale="Reds",
        zmin=0, zmax=25,
        colorbar_title="% diabetic",
        marker_line_color="white",
        marker_line_width=0.5,
    ))
    fig.update_layout(
        title_text="State-level diabetes risk — BRFSS 2024 (real data coming)",
        geo_scope="usa",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        font=dict(family="DM Sans"),
    )
    map_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("predictions.html", map_json=map_json)
