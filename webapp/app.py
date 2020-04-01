import datetime

from flask import Flask, render_template
from webapp.api.wine import Wine, StockCounter, StockDataFetcher
from constants import Colours

app = Flask(__name__)

stock = StockDataFetcher(counter=StockCounter(use_cached=True),
                         refresh_interval=datetime.timedelta(hours=1))


@app.route('/')
def upload_page():
    top_wines = stock.counter.stock_change_df.iloc[:5]
    sales = stock.counter.sales_by_wine_type
    total_sales = sum([v for v in sales.values()])
    percentages = {k: int(v/total_sales*100) for k, v in sales.items()}

    wines = [Wine(row.wine_name, row.wine_img, row.stock_change) for i, row in top_wines.iterrows()]
    return render_template('home.html',
                           top_wines=wines,
                           red_percentage=percentages['red'],
                           white_percentage=percentages['white'],
                           rose_percentage=percentages['rose'],
                           red=Colours.red,
                           white=Colours.white,
                           rose=Colours.rose,
                           radius='50px')


if __name__ == "__main__":
    app.run(debug=True)
