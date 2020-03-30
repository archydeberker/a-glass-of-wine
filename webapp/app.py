import random

from flask import Flask, render_template
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
    def __init__(self):
        self.name = random.choice(['Bigfoot', 'Pino Grigio', 'Tasty Toots', 'Smashing Stuff', 'Fab Five'])
        self.img  = random.choice(IMGs)
        # self.consumption = random.choice('')


@app.route('/')
def upload_page():
    return render_template('home.html', top_wines=[Wine(), Wine(), Wine(), Wine(), Wine()])


if __name__ == "__main__":
    app.run(debug=True)
