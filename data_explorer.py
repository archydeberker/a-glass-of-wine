import streamlit as st
from data import analysis
import plotly.express as px


@st.cache
def load_data():
    counter = analysis.StockCounter()
    return counter


def filter_df(df, wine_names):
    return df.loc[df['wine_name'].isin(wine_names)]


counter = load_data()

wine_names = st.sidebar.multiselect(options=counter.stock_change_df.sort_values(by='stock_change')['wine_name'].unique(), label='Wine')

st.header('All wines stock change')
fig = px.bar(counter.stock_change_df, x='wine_name', y='stock_change')
st.write(fig)

fig = px.line(filter_df(counter.online_df, wine_names), x='timestamp', y='stock', color='wine_name')
st.write(fig)

st.write(filter_df(counter.online_df, wine_names))
st.write(filter_df(counter.stock_change_df, wine_names))