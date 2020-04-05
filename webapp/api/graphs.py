import json
import datetime

import pandas as pd
import numpy as np
import plotly
from plotly import graph_objects as go
import plotly.express as px
from constants import Colours


def map_wines(counter):

    country_df = counter.stock_change_df.groupby('wine_origin_now').sum()
    country_df['country'] = country_df.index
    country_df['Bottles Sold Today'] = abs(country_df['stock_change'])

    # Use this to get country information
    df = px.data.gapminder().query("year==2007")
    df = df[['country', 'iso_alpha']]
    # df['color'] = Colours.red
    df.set_index('country', inplace=True)
    country_df = country_df.join(df, rsuffix='_')
    fig = px.scatter_geo(country_df,
                         locations="iso_alpha",
                         size="Bottles Sold Today",
                         hover_name="country",
                         hover_data=["Bottles Sold Today"])

    fig.update_layout(
        geo=dict(
            landcolor='rgb(240, 240, 240)',
            showframe=False,
            coastlinecolor='white',
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def plot_cases(df):

    # move to constants and import?
    colors = {'hospitalized': 'rgba(232, 230, 235,1)',
              'recovered': 'rgba(112, 55, 71,1)',
              'cases': 'rgba(211, 176, 245,1)',
              'deaths': 'rgba(0, 0, 0,1)'}
    case_types = ['deaths', 'recovered', 'cases']

    fig = go.Figure()

    for case_type in case_types:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[case_type],
            hoverinfo='x+y',
            mode='lines',
            line=dict(width=0.5, color=colors[case_type]),
            fillcolor=colors[case_type],
            stackgroup='one',
            name=case_type
        ))

    fig.update_layout(
        title={
            'text': "Our curve",
            'y': 0.9,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top'},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Grey')

    case_graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return case_graphJSON


def example_graph():
    # Method from https://code.tutsplus.com/tutorials/charting-using-plotly-in-python--cms-30286

    count = 500
    xScale = np.linspace(0, 100, count)
    yScale = np.random.randn(count)

    # Create a trace
    trace = go.Scatter(
        x=xScale,
        y=yScale
    )

    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON