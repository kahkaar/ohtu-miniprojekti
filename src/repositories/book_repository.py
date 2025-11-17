from sqlalchemy import text

from config import db
from entities.book import Book


def get_books():
    query = text(
        "SELECT id, title, author, year, publisher, address FROM book")
    result = db.session.execute(query)
    books = result.fetchall()
    return [Book(book[0], book[1], book[2], book[3], book[4], book[5]) for book in books]

def create_book(title, author, year, publisher, address):
    """Creates a new book entry in the database"""
    sql = text("""INSERT INTO book (title, author, year, publisher, address)
          VALUES (:title, :author, :year, :publisher, :address)""")
    db.session.execute(sql, {
        "title": title,
        "author": author,
        "year": year,
        "publisher": publisher,
        "address": address
    })
    db.session.commit()
