import datetime

from flask import Flask, render_template

from webapp.api.graphs import map_wines, plot_cases
from webapp.api.wine import Wine, StockCounter, glasses_sold_yesterday
from webapp.api.utils import DataFetcher
from webapp.api.cases import CaseData
from constants import Colours, CASE_CITATION

app = Flask(__name__)

stock = DataFetcher(data_object=StockCounter(use_cached=True),
                    refresh_interval=datetime.timedelta(hours=1))

cases = DataFetcher(data_object=CaseData(use_cached=True),
                    refresh_interval=datetime.timedelta(hours=1))


@app.route('/')
def upload_page():
    top_wines = stock.latest_data.stock_change_df.iloc[:5]
    sales = stock.latest_data.sales_by_wine_type
    total_sales = sum([v for v in sales.values()])
    percentages = {k: int(v/total_sales*100) for k, v in sales.items()}

    wines = [Wine(row.wine_name, row.wine_img, row.stock_change) for i, row in top_wines.iterrows()]

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
                           data_citation=CASE_CITATION)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
