from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# For an explanation of the models and relationships defined here, see
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/


class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(100))
    img_url = db.Column(db.String(100))
    url = db.Column(db.String(100))
    stock = db.relationship('Stock', backref='wine', lazy=True)

    def __repr__(self):
        return f"<{self.id}: {self.name}, {self.type}>"


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    value = db.Column(db.Integer)
    wine_id = db.Column(db.Integer, db.ForeignKey("wine.id"), nullable=False)

