import streamlit as st

from constants import COUNTRIES_TO_GRAPH
from webapp.api.cases import CaseData, get_df_for_country
from webapp.api.graphs import plot_log_daily
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

options = list(counter.stock_change_df.sort_values(by='stock_change', ascending=False   )['wine_name'].unique())
wine_names = st.sidebar.multiselect(options=options, label='Wine', default=options[0])

st.header('All wines stock change')
fig = px.bar(counter.stock_change_df, x='wine_name', y='stock_change')
st.write(fig)
st.write(counter.stock_change_df.head(10))

_df = counter.stock_change_df.copy()
_df.dropna(inplace=True, subset=['wine_type_now'])
# _df = _df.groupby('wine_type_now').sum()
fig = px.bar(_df, x='wine_type_now', y='stock_change')
st.write(fig)


_df = _df.groupby('wine_type_now').sum()
st.write(_df)
st.write({'red': _df.loc['Red wine']['stock_change'],
          'white': _df.loc['White wine']['stock_change'],
          'rose': _df.loc['Rosé']['stock_change'],
          })

all_data_df = counter.online_df.copy()

all_data_df['date'] = all_data_df['timestamp'].apply(lambda x: x.date())
sales_by_type = all_data_df.groupby(['date', 'wine_type'])['wine_consumption'].sum().reset_index()
st.write(sales_by_type)
fig = px.line(sales_by_type, x='date', y='wine_consumption', color='wine_type')
st.write(fig)

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

st.write('Stock')
fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='stock', color='wine_name')
st.write(fig)
st.write('Consumption')
fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='wine_consumption', color='wine_name')
st.write(fig)
st.write('Cumulative consumption')
fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='cumulative_wine_consumption', color='wine_name')
st.write(fig)



st.write(filter_df(counter.online_df, wine_names))
st.write(filter_df(counter.stock_change_df, wine_names))

st.header('By colour')
_new_data = counter.online_df.dropna(subset=['wine_type']).groupby(['timestamp', 'wine_type']).sum().reset_index()
st.write(_new_data)
fig = px.line(_new_data, x='timestamp', y='stock', color='wine_type', template="plotly_white")
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

countries = [get_df_for_country(c) for c in COUNTRIES_TO_GRAPH]

combined = pd.concat(countries)

st.write(combined)

st.write(plot_log_daily(combined, 'confirmed', x_axis='days_since_30'))
st.write(plot_log_daily(combined, 'deaths', x_axis='days_since_3'))

st.write(plot_log_daily(combined, 'confirmed', x_axis='days_since_30', y_axis='rolling_daily_count_change', log=False))
st.write(plot_log_daily(combined, 'deaths', x_axis='days_since_3', y_axis='rolling_daily_count_change', log=False))

