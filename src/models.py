from config import db  

class Book(db.Model):
    __tablename__ = "book"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    author = db.Column(db.Text)
    year = db.Column(db.Integer)
    publisher = db.Column(db.Text)
    address = db.Column(db.Text)
