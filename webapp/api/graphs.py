import json

import numpy as np

from constants import Colours
import plotly
from plotly import graph_objects as go, express as px
import plotly.express as px
import datetime
import pandas as pd


def encode_as_json(fig):
    return json.dumps(fig, cls = plotly.utils.PlotlyJSONEncoder)


def map_wines(counter):
    # Method from https://code.tutsplus.com/tutorials/charting-using-plotly-in-python--cms-30286

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
                         hover_data=["Bottles Sold Today"],
                         color_discrete_sequence=[Colours.red])

    fig.update_layout(
        geo=dict(
            landcolor='rgb(240, 240, 240)',
            showframe=False,
            coastlinecolor='white',
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def plot_cases(df, return_fig=False):

    df = df.loc[df['date'] > pd.Timestamp(datetime.date(year=2020, month=3, day=22))]
    # move to constants and import?
    colors = {'hospitalized': 'rgba(232, 230, 235,1)',
              'recovered': 'rgba(112, 55, 71,.5)',
              'cases': 'rgba(170, 176, 200,0.3)',
              'deaths': 'rgba(0, 0, 0,1)'}
    case_types = ['deaths', 'recovered', 'cases']

    fig = go.Figure()

    for case_type in case_types:
        fig.add_trace(go.Scatter(
            x=df.date,
            y=df[case_type],
            hovertemplate='%{x}: %{y}',
            mode='lines',
            line=dict(width=0.5, color=colors[case_type]),
            fillcolor=colors[case_type],
            stackgroup='one',
            name=case_type
        ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation='h',
        legend=dict(x=-.1, y=1.2),
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.51)')

    if return_fig:
        return fig

    case_graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return case_graphJSON


def plot_log_daily(df, status, x_axis='days_since_3', y_axis='rolling_daily_count', log=True,
                   x_axis_title=None, y_axis_title=None):
    df.reset_index()

    # Get rid of data before day 0
    df = df.loc[df[x_axis] >= 0]
    df = df.loc[df['status'] == status]

    colors = 4*['rgba(0,0,0,.2)',
                ] + ['rgba(127,0,0,.9)',
                     'rgba(0,0,50,.5)',
                     'rgba(0,0,50,.5)',
                     'rgba(0,0,50,.5)']

    font_colors = 4*['rgba(0,0,0,.6)',
                ] + ['rgba(127,0,0,1)',
                     'rgba(0,0,50,.6)',
                     'rgba(0,0,50,.6)',
                     'rgba(0,0,50,.6)']

    fig = px.line(df,
                  x=x_axis,
                  y=y_axis,
                  color='country',
                  template='plotly_white',
                  color_discrete_sequence=colors)

    for i, country in enumerate(df.country.unique()):
        last_row = df.loc[df['country'] == country].iloc[-1]
        fig.add_annotation(x=last_row[x_axis],
                           y=np.log10(last_row[y_axis]) if log else last_row[y_axis],
                           xanchor="left",
                           text=country,
                           font=dict(
                               color=font_colors[i],
                               size=13,
                           ))

    if log:
        fig.update_layout(yaxis_type="log", showlegend=False)

    fig.update_layout(xaxis_title=x_axis_title or x_axis,
                      yaxis_title=y_axis_title or y_axis,
                      )

    fig.update_annotations(dict(
        xref="x",
        yref="y",
        showarrow=False,
    ))

    return fig