import streamlit as st

import webapp.api.wine
from data import analysis
import plotly.express as px


@st.cache
def load_data():
    counter = webapp.api.wine.StockCounter()
    return counter


def filter_df(df, wine_names):
    return df.loc[df['wine_name'].isin(wine_names)]


counter = load_data()

options = counter.stock_change_df.sort_values(by='stock_change')['wine_name'].unique()
wine_names = st.sidebar.multiselect(options=options, label='Wine')

st.header('All wines stock change')
fig = px.bar(counter.stock_change_df, x='wine_name', y='stock_change')
st.write(fig)

fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='stock', color='wine_name')
st.write(fig)

st.write(filter_df(counter.online_df, wine_names))
st.write(filter_df(counter.stock_change_df, wine_names))

st.header('By colour')
fig = px.area(counter.online_df, x='timestamp', y='stock_change', color='wine_type_now')
# st.header('By origin')