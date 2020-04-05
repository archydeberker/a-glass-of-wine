import datetime

import requests
import streamlit as st

from webapp.api.cases import CaseData
from webapp.api.wine import StockCounter
from webapp.api import graphs

import plotly.express as px
import constants
import numpy as np
import pandas as pd


@st.cache
def load_data():
    counter = StockCounter(use_cached=True, local_path='/Users/archydeberker/Desktop/code/saq/scripts/online_data_latest.csv')
    return counter


@st.cache
def load_case_data():
    cases = CaseData(use_cached=True, local_path='/Users/archydeberker/Desktop/code/saq/scripts/canada_case_data_latest.csv')
    return cases


def filter_df(df, wine_names):
    return df.loc[df['wine_name'].isin(wine_names)]


counter = load_data()

options = list(counter.stock_change_df.sort_values(by='stock_change')['wine_name'].unique())
wine_names = st.sidebar.multiselect(options=options, label='Wine', default=options[0])

st.header('All wines stock change')
fig = px.bar(counter.stock_change_df, x='wine_name', y='stock_change')
st.write(fig)

_df = counter.stock_change_df.copy()
_df.dropna(inplace=True, subset=['wine_type_now'])
# _df = _df.groupby('wine_type_now').sum()
fig = px.bar(_df, x='wine_type_now', y='stock_change')
st.write(fig)

_df = counter.stock_change_df.copy()
_df.dropna(inplace=True, subset=['wine_type_now'])
_df = _df.groupby('wine_type_now').sum()
st.write(_df)
st.write({'red': _df.loc['Red wine']['stock_change'],
          'white': _df.loc['White wine']['stock_change'],
          'rose': _df.loc['Rosé']['stock_change'],
          })

# Wine origin graph
country_df = counter.stock_change_df.groupby(['wine_origin_now', 'wine_type_now']).sum().reset_index()
country_df['stock_change'] = abs(country_df['stock_change'])

# Use this to get country information
df = px.data.gapminder().query("year==2007")
df = df[['country', 'iso_alpha']]
df.set_index('country', inplace=True)
country_df.set_index('wine_origin_now', inplace=True)
country_df = country_df.join(df, rsuffix='_')
country_df = country_df.reset_index()
st.write(country_df)
fig = px.scatter_geo(country_df,
                     locations="iso_alpha",
                     size="stock_change",
                     hover_name="index",
                     color='wine_type_now',
                     color_discrete_sequence=[constants.Colours.red,
                                              constants.Colours.white,
                                              constants.Colours.rose,
                                              ])

fig.update_layout(

    geo=dict(
        landcolor='rgb(240, 240, 240)',
        showframe=False,
        coastlinecolor='white',
    )
)
st.write(fig)

fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='stock', color='wine_name')
st.write(fig)

st.write(filter_df(counter.online_df, wine_names))
st.write(filter_df(counter.stock_change_df, wine_names))

st.header('By colour')
_new_data = counter.online_df.dropna(subset=['wine_type']).groupby(['timestamp', 'wine_type']).sum().reset_index()
st.write(_new_data)
fig = px.area(_new_data, x='timestamp', y='stock', color='wine_type', template="plotly_white")
st.write(fig)

cases = load_case_data()

st.write(cases.case_df)
log_df = cases.case_df.copy()

log_df = log_df.select_dtypes(include=['number']).apply(np.log).join(cases.case_df['date'])
fig = graphs.plot_cases(log_df, return_fig=True)
st.write(fig)
#
# log_df.rename({'cases': 'sum_cases',
#                'deaths': 'sum_deaths',
#                'recovered': 'sum_recovered'},
#               axis=1,
#               inplace=True)
st.write(log_df)
log_df = pd.melt(log_df,
                 id_vars='date',
                 value_vars=['cases', 'deaths', 'recovered'],
                 var_name='status',
                 value_name='sum')


st.write(px.line(log_df, x='date', y='sum', color='status'))


country_dict = {'Canada': 36, 'Italy': 137, 'South Korea': 143,
                'Hubei': 62, 'France': 116, 'Quebec': 44, 'US': 225,
                'Alberta': 35,
                'British Columbia': 36,
                'Manitoba': 38,
                'New Brunswick': 39,
                'Newfoundland & Labrador': 40,
                'Nova Scotia': 41,
                'Ontario': 42,
                'PEI': 43,
                'Saskatchewan': 45,
                'Yukon': 256,
                }

base_URL = ' https://coronavirus-tracker-api.herokuapp.com/v2/locations'


def days_since_start_point(df, threshold=100):
    """ Get the timepoint to use as a threshold for days since X"""

    idx = df['sum'].apply(lambda x: abs(x-threshold)).argmin()

    return np.arange(len(df)) - idx


@st.cache
def get_df_for_country(name):
    response = requests.get(f"{base_URL}/{country_dict[name]}")
    j = response.json()['location']

    out = []
    for status in ['confirmed', 'deaths']:
        timeline = j['timelines'][status]['timeline']
        _df = pd.DataFrame.from_dict(timeline, orient='index', columns=['sum'])
        _df['status'] = status
        _df['daily_count'] = _df['sum'].diff()
        _df['daily_count_change'] = _df['daily_count'].diff()
        _df['rolling_daily_count'] = _df['daily_count'].rolling(7).mean()
        _df['rolling_daily_count_change'] = _df['daily_count_change'].rolling(7).mean()
        _df['days_since_100'] = days_since_start_point(_df, threshold=100)
        _df['days_since_30'] = days_since_start_point(_df, threshold=30)
        _df['days_since_3'] = days_since_start_point(_df, threshold=3)

        out.append(_df)

    df = pd.concat(out)

    df['country'] = name

    return df


def plot_log_daily(df, status, x_axis='days_since_3', y_axis='rolling_daily_count', log=True):
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
        fig.update_layout(yaxis_type="log", showlegend=False, title=dict(text=status))

    fig.update_annotations(dict(
        xref="x",
        yref="y",
        showarrow=False,
    ))

    st.write(fig)


countries = [get_df_for_country(c) for c in ['Italy', 'Hubei', 'South Korea',
                                             'US', 'Quebec', 'British Columbia',
                                             'Ontario', 'Alberta']]

combined = pd.concat(countries)
combined['rolling_daily_count'] = combined['daily_count'].rolling(7).mean()

st.write(combined)

plot_log_daily(combined, 'confirmed', x_axis='days_since_30')
plot_log_daily(combined, 'deaths', x_axis='days_since_3')

plot_log_daily(combined, 'confirmed', x_axis='days_since_30', y_axis='rolling_daily_count_change', log=False)
plot_log_daily(combined, 'deaths', x_axis='days_since_3', y_axis='rolling_daily_count_change', log=False)

