import json

import numpy as np
import plotly
from plotly import graph_objects as go
import plotly.express as px
from constants import Colours


def map_wines(counter):
    country_df = counter.stock_change_df.groupby(['wine_origin_now', 'wine_type_now']).sum().reset_index()
    country_df['stock_change'] = abs(country_df['stock_change'])

    # Use this to get country information
    df = px.data.gapminder().query("year==2007")
    df = df[['country', 'iso_alpha']]
    df.set_index('country', inplace=True)
    country_df.set_index('wine_origin_now', inplace=True)
    country_df = country_df.join(df, rsuffix='_')
    country_df = country_df.reset_index()

    # Renaming to make the plot look nicer
    country_df.rename({'wine_type_now': 'Type',
                       'stock_change': 'Bottles Sold',
                       'iso_alpha': 'Country'},
                        inplace=True, axis=1)

    fig = px.scatter_geo(country_df,
                         locations="Country",
                         size="Bottles Sold",
                         hover_name="index",
                         color='Type',
                         color_discrete_sequence=[Colours.red,
                                                  Colours.white,
                                                  Colours.rose,
                                                  ])

    fig.update_layout(

        geo=dict(
            landcolor='rgb(240, 240, 240)',
            showframe=False,
            coastlinecolor='white',
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


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