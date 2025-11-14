from config import db
from sqlalchemy import text

from entities.todo import Book

def get_books():
    result = db.session.execute(text("SELECT id, title, author, year, publisher, address FROM book"))
    books = result.fetchall()
    return [Book(book[0], book[1], book[2], book[3], book[4], book[5]) for book in books]
