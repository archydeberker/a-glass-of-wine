import random

from flask import Flask, render_template
from data.analysis import StockCounter

app = Flask(__name__)


class Wine:
    def __init__(self, name, img, sales):
        self.name = name
        self.img = self._format_img(img)
        self.sales = int(abs(sales))

    def _format_img(self, img_url):
        img_url = img_url.split('?')[0]
        img_url += '?quality=80&fit=bounds&height=166&width=111&canvas=111:166'
        return img_url


# TODO: how do we refresh this guy? Better save something light to disk
counter = StockCounter()


@app.route('/')
def upload_page():
    top_wines = counter.stock_change_df.iloc[:5]
    wines = [Wine(row.wine_name, row.wine_img, row.stock_change) for i, row in top_wines.iterrows()]
    return render_template('home.html', top_wines=wines)


if __name__ == "__main__":
    app.run(debug=True)
