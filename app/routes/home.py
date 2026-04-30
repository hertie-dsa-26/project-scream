from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly, json

home_bp = Blueprint("home", __name__)

# All US state abbreviations for the choropleth base layer
_STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
]


@home_bp.route("/")
@home_bp.route("/home")
def home():
    # Placeholder choropleth — values will be replaced with real BRFSS diabetes rates
    fig = go.Figure(go.Choropleth(
        locations=_STATES,
        z=[0] * len(_STATES),          # swap in real data later
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
    map_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("home.html", map_json=map_json)
