import json

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