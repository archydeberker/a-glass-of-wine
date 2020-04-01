import streamlit as st

import webapp.api.wine
from data import analysis
import plotly.express as px
import constants


@st.cache
def load_data():
    counter = webapp.api.wine.StockCounter(use_cached=True)
    return counter


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

country_df = counter.stock_change_df.groupby('wine_origin_now').sum()
country_df['country'] = country_df.index
country_df['stock_change'] = abs(country_df['stock_change'])

# Use this to get country information
df = px.data.gapminder().query("year==2007")
df = df[['country', 'iso_alpha']]
df.set_index('country', inplace=True)
country_df = country_df.join(df, rsuffix='_')
country_df['color'] = constants.Colours.red
st.write(country_df)
fig = px.scatter_geo(country_df,
                     locations="iso_alpha",
                     size="stock_change",
                     hover_name="country",
                     color='color')

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
fig = px.area(counter.online_df, x='timestamp', y='stock_change', color='wine_type_now')
# st.header('By origin')
