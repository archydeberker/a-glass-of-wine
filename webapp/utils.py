import datetime
import time
import pandas as pd
import plotly.express as px
import seaborn as sns


def filter_df(df, wine_names):
    return df.loc[df['wine_name'].isin(wine_names)]