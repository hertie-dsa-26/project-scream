from flask import Blueprint, render_template
import plotly.graph_objs as go
import plotly, json
from app.utils.data import load_brfss

vis_bp = Blueprint('vis', __name__)

@vis_bp.route('/vis')
def vis():
    df = load_brfss()

    # --- Data prep (same logic as notebook) ---
    depression_labels = {1: "Yes", 2: "No", 7: "Don't know/Not sure", 9: "Refused"}
    counts = df['has_depression'].map(depression_labels).value_counts()
    pcts   = counts / counts.sum() * 100

    labels = counts.index.tolist()
    colors = ['#e74c3c', '#2ecc71', '#95a5a6', '#bdc3c7']

    # --- Two traces: one for counts, one for percentages ---
    trace_counts = go.Bar(
        x=labels,
        y=counts.values.tolist(),
        marker_color=colors,
        text=[f"{v:,.0f}" for v in counts.values],
        textposition='outside',
        visible=True,
        name='Count'
    )
    trace_pcts = go.Bar(
        x=labels,
        y=[round(p, 1) for p in pcts.values],
        marker_color=colors,
        text=[f"{p:.1f}%" for p in pcts.values],
        textposition='outside',
        visible=False,   # hidden by default
        name='Percentage'
    )

    # --- Toggle button ---
    updatemenus = [{
        'type': 'buttons',
        'direction': 'right',
        'x': 0.0, 'y': 1.15,
        'buttons': [
            {
                'label': 'Counts',
                'method': 'update',
                'args': [{'visible': [True, False]},
                         {'yaxis': {'title': 'Number of Respondents'}}]
            },
            {
                'label': 'Percentages',
                'method': 'update',
                'args': [{'visible': [False, True]},
                         {'yaxis': {'title': '% of Respondents'}}]
            }
        ]
    }]

    layout = go.Layout(
        title='Fig. 1: (Ever told) you had a depressive disorder',
        yaxis=dict(title='Number of Respondents'),
        xaxis=dict(title='Response'),
        updatemenus=updatemenus,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=100)
    )

    fig = go.Figure(data=[trace_counts, trace_pcts], layout=layout)
    chart1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('vis.html', chart1=chart1)