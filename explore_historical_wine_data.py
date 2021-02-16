import datetime

import streamlit as st

from constants import Colours
from webapp.api.wine import StockCounter

import plotly.express as px
import pandas as pd

from webapp.utils import filter_df


@st.cache
def load_all_online_data():
    historical_online_data = '/Users/archydeberker/Desktop/code/saq/scripts/online_data_latest.csv'
    df = pd.read_csv(historical_online_data,
                     parse_dates=['timestamp'],
                     dtype={'wine_name': 'object',
                            'id': 'int64',
                            'stock': 'int64',
                            'timestamp': 'str',
                            'wine_img': 'str'})

    df['date'] = df['timestamp'].apply(lambda x: x.date())
    df['hour'] = df['timestamp'].apply(lambda x: x.hour)
    df['timestamp_hour'] = df['timestamp'].apply(lambda x: datetime.datetime.combine(x.date(),
                                                                                     datetime.time(hour=x.hour)),

                                                 )
    counter = StockCounter(df)
    return counter


counter = load_all_online_data()
options = list(counter.stock_change_df.sort_values(by='stock_change', ascending=False)['wine_name'].unique())
wine_names = st.sidebar.multiselect(options=options, label='Wine', default=options[0])


st.title('All historical data')

st.subheader('Stock change for the most popular wine the period')
fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='stock', color='wine_name')
st.write(fig)
st.write('Consumption')
fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='wine_consumption', color='wine_name')
st.write(fig)
st.write('Cumulative consumption')
fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='cumulative_wine_consumption', color='wine_name')
st.write(fig)


st.subheader('Top 10 wines for the last fortnight, using stock change')
top = counter.stock_change_df.iloc[:10]
fig = px.bar(top, x='wine_name', y='stock_change')
st.write(fig)

alt_top = counter.online_df.groupby('id')['wine_consumption'].sum()
alt_top = alt_top.reset_index()
alt_top = alt_top.join(counter.online_df[['wine_type', 'wine_name']], on='id')
alt_top.sort_values(by='wine_consumption', inplace=True, ascending=False)
st.write(alt_top.iloc[0:100])

fig = px.bar(alt_top.iloc[0:10].reset_index(), y='wine_name', x='wine_consumption', color='wine_type', orientation='h',
             template='plotly_white', color_discrete_sequence=[Colours.white, Colours.red],
             title='Consumption 29th March - 12th April 2020', width=1000)
fig.update_yaxes(categoryorder='total descending')
fig.update_layout(margin={'l': 300, "r": 100},
                  xaxis_title='Wine Consumption (Bottles)',
                  yaxis_title=None)
st.write(fig)

st.header('Colours over time')

alt_top = counter.online_df.groupby(['timestamp_hour', 'wine_type'])['wine_consumption'].sum()
alt_top = alt_top.reset_index()
st.write(alt_top)
fig = px.line(alt_top.reset_index(), y='wine_consumption', x='timestamp_hour', color='wine_type',
             template='plotly_white', color_discrete_sequence=[Colours.red, Colours.white, Colours.rose],
             title='Consumption 29th March - 12th April 2020', width=1000)
fig.update_yaxes(categoryorder='total descending')
fig.update_layout(margin={'l': 300, "r": 100},
                  xaxis_title='Wine Consumption (Bottles)',
                  yaxis_title=None)
st.write(fig)


st.header('Animation')
st.write('Does not work well because plotly does not like things dropping out of the date sequence')
# top_over_time = counter.online_df.groupby(['date', 'id'])['wine_consumption'].sum()
# top_over_time = top_over_time.reset_index()
# top_over_time = top_over_time.join(counter.online_df[['wine_type', 'wine_name']], on='id')
# top_over_time.sort_values(by=['date', 'wine_consumption'], inplace=True, ascending=False)
# top_over_time.reset_index(inplace=True)
# top_over_time.dropna(how='any', inplace=True)
# st.write(top_over_time.reset_index())
# for date in top_over_time['date'].unique():
#     _df = top_over_time.loc[top_over_time['date'] == date].iloc[:10]
#     fig = px.bar(_df.reset_index(), y='wine_name', x='wine_consumption', orientation='h',
#              color='wine_type',
#              template='plotly_white', color_discrete_sequence=[Colours.white, Colours.red],
#              width=1000)
#     fig.update_yaxes(categoryorder='total descending')
#     fig.update_layout(margin={'l': 300, "r": 100},
#                       xaxis_title='Wine Consumption (Bottles)',
#                       yaxis_title=None)
#     st.write(fig)




######
st.subheader('24 hour rolling average of glasses consumed')
consumption_per_hour = counter.online_df.groupby('timestamp')['wine_consumption'].sum()
consumption_per_hour = pd.DataFrame(consumption_per_hour)
consumption_per_hour['rolling_24'] = consumption_per_hour.rolling(24).sum()
st.write(consumption_per_hour)
fig = px.line(consumption_per_hour.reset_index(), x='timestamp', y='rolling_24')
st.write(fig)

st.write(filter_df(counter.online_df, wine_names))
st.write(filter_df(counter.stock_change_df, wine_names))

st.header('By colour')
_new_data = counter.online_df.dropna(subset=['wine_type']).groupby(['timestamp', 'wine_type']).sum().reset_index()
_new_data['alt_cum_con'] = _new_data.groupby(['wine_type'])['wine_consumption'].cumsum()
st.write(_new_data)
fig = px.line(_new_data, x='timestamp', y='stock', color='wine_type', template="plotly_white")
st.write(fig)

st.header('Cumulative consumption on log plot')

fig = px.line(_new_data, x='timestamp', y='alt_cum_con', color='wine_type', template="plotly_white")
fig.update_layout(yaxis_type="log", showlegend=False)
st.write(fig)
