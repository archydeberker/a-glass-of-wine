import datetime
import os
from functools import lru_cache

from flask import Flask, render_template

from webapp.api.graphs import map_wines, plot_cases, plot_log_daily, encode_as_json
from webapp.api.wine import Wine, StockCounter
from webapp.api.utils import DataFetcher
from webapp.api.cases import CaseData, get_cases_from_api
from constants import Colours, CASE_CITATION, CASE_API_GITHUB
from webapp.content import ContentEn, ContentFr

app = Flask(__name__)

local = os.path.exists('/Users/archydeberker')
case_local_path = '/Users/archydeberker/Desktop/code/saq/scripts/canada_case_data_latest.csv' if local else None


def _format_integer(number: float):
    return f"{int(number):,}"


@lru_cache(128)
def get_stock_data():
    return DataFetcher(data_object=StockCounter(),
                       refresh_interval=datetime.timedelta(hours=1))


@lru_cache(128)
def get_cases_data():
    return DataFetcher(data_object=CaseData(use_cached=True, local_path=case_local_path),
                       refresh_interval=datetime.timedelta(hours=1))


@app.route('/')
@app.route('/<language>')
def home_page(language='en'):
    cases = get_cases_data()
    stock = get_stock_data()

    top_wines = stock.latest_data.stock_change_df.iloc[:5]
    sales = stock.latest_data.sales_by_wine_type
    total_sales = sum([v for v in sales.values()])
    percentages = {k: int(v/total_sales*100) for k, v in sales.items()}

    wines = [Wine(row.wine_name, row.wine_img, row.stock_change) for i, row in top_wines.iterrows()]
    international_cases_df = get_cases_from_api()

    confirmed = plot_log_daily(international_cases_df, 'confirmed', x_axis='days_since_30',
                               x_axis_title='Days since 30 cases',
                               y_axis_title='Daily new cases (smoothed)')
    deaths = plot_log_daily(international_cases_df, 'deaths', x_axis='days_since_3',
                            x_axis_title='Days since 3 deaths',
                            y_axis_title='Daily deaths (smoothed)')
    deaths.update_layout(margin=dict(t=0))
    days_since_lockdown_started = (datetime.datetime.now().date() - datetime.date(year=2020, month=3, day=22)).days

    if language == 'en':
        content = ContentEn(days_since_lockdown_started, _format_integer(stock.latest_data.glasses_sold))
    else:
        content = ContentFr(days_since_lockdown_started, _format_integer(stock.latest_data.glasses_sold))

    return render_template('home.html',
                           french=language == 'fr',
                           content=content,
                           days_since_lockdown_started=days_since_lockdown_started,
                           top_wines=wines,
                           red_percentage=percentages['red'],
                           white_percentage=percentages['white'],
                           rose_percentage=percentages['rose'],
                           red=Colours.red,
                           white=Colours.white,
                           rose=Colours.rose,
                           radius='50px',
                           graphJSON=map_wines(stock.latest_data),
                           case_graphJSON=plot_cases(cases.latest_data.case_df),
                           confirmed_graphJSON=encode_as_json(confirmed),
                           deaths_graphJSON=encode_as_json(deaths),
                           data_citation=CASE_CITATION,
                           case_api_citation=CASE_API_GITHUB)


if __name__ == "__main__":
    # When run via the command line during development, debug mode triggers usage of local files
    # This will not be the case when run with gunicorn in prod

    app.debug = True
    app.run(debug=True, port=5001)
