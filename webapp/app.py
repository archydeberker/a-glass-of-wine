import datetime

from flask import Flask, render_template

from webapp.api.graphs import map_wines, plot_cases, plot_log_daily, encode_as_json
from webapp.api.wine import Wine, StockCounter, glasses_sold_yesterday
from webapp.api.utils import DataFetcher
from webapp.api.cases import CaseData, get_cases_from_api
from constants import Colours, CASE_CITATION, CASE_API_GITHUB
import os

app = Flask(__name__)

local = os.path.exists('/Users/archydeberker')
wine_local_path = '/Users/archydeberker/Desktop/code/saq/scripts/online_data_latest.csv' if local else None
case_local_path = '/Users/archydeberker/Desktop/code/saq/scripts/canada_case_data_latest.csv' if local else None

stock = DataFetcher(data_object=StockCounter(use_cached=True, local_path=wine_local_path),
                    refresh_interval=datetime.timedelta(hours=1))

cases = DataFetcher(data_object=CaseData(use_cached=True, local_path=case_local_path),
                    refresh_interval=datetime.timedelta(hours=1))


@app.route('/')
def home_page():
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

    return render_template('home.html',
                           top_wines=wines,
                           glasses_sold=glasses_sold_yesterday(stock.latest_data.stock_change_df),
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
