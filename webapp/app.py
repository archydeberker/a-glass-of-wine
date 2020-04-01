import datetime

from flask import Flask, render_template
from webapp.api.wine import Wine, StockCounter, StockDataFetcher

app = Flask(__name__)

stock = StockDataFetcher(counter=StockCounter(use_cached=True),
                         refresh_interval=datetime.timedelta(hours=1))


@app.route('/')
def upload_page():
    top_wines = stock.counter.stock_change_df.iloc[:5]
    wines = [Wine(row.wine_name, row.wine_img, row.stock_change) for i, row in top_wines.iterrows()]
    return render_template('home.html', top_wines=wines)


if __name__ == "__main__":
    app.run(debug=True)
