import json
from constants import Colours
import plotly
from plotly import graph_objects as go
import plotly.express as px
import datetime
import pandas as pd


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


def plot_cases(df):

    df = df.loc[df['date'] > pd.Timestamp(datetime.date(year=2020, month=3, day=22))]
    # move to constants and import?
    colors = {'hospitalized': 'rgba(232, 230, 235,1)',
              'recovered': 'rgba(112, 55, 71,1)',
              'cases': 'rgba(211, 176, 245,1)',
              'deaths': 'rgba(0, 0, 0,1)'}
    case_types = ['deaths', 'recovered', 'cases']

    fig = go.Figure()

    for case_type in case_types:
        fig.add_trace(go.Scatter(
            x=df.date,
            y=df[case_type],
            hoverinfo='x+y',
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

    case_graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return case_graphJSON
