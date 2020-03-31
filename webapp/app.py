import random

from flask import Flask, render_template
from data.analysis import StockCounter

app = Flask(__name__)


IMGs = ['https://www.saq.com/media/catalog/product/1/4/14207918-1_1578553820.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166',
        'https://www.saq.com/media/catalog/product/1/2/12862898-1_1578412216.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166',
        'https://www.saq.com/media/catalog/product/1/2/12565527-1_1578346517.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166',
        'https://www.saq.com/media/catalog/product/1/4/14220389-1_1580352612.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166',
        'https://www.saq.com/media/catalog/product/1/1/11315497-1_1584984920.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166',
        'https://www.saq.com/media/catalog/product/1/1/11509582-1_1580666712.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166'
        'https://www.saq.com/media/catalog/product/1/4/14148532-1_1578552625.png?quality=80&fit=bounds&height=166&width=111&canvas=111:166'
        ]


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
