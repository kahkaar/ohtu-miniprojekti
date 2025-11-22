from sqlalchemy import text

from config import db
from entities.book import Book


def get_books():
    query = text(
        "SELECT id, title, author, year, publisher, address FROM book")
    result = db.session.execute(query)
    books = result.fetchall()
    return [Book(book[0], book[1], book[2], book[3], book[4], book[5]) for book in books]


def get_book(id):
    """Fetches a single book by its ID from the database"""
    sql = text("""
        SELECT id, title, author, year, publisher, address
        FROM book WHERE id = :id
    """)
    result = db.session.execute(sql, {"id": id}).fetchone()
    if result is None:
        return None
    return Book(result[0], result[1], result[2], result[3], result[4], result[5])


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


def update_book(id, title, author, year, publisher, address):
    sql = text("""
        UPDATE book
        SET title = :title,
            author = :author,
            year = :year,
            publisher = :publisher,
            address = :address
        WHERE id = :id
    """)
    db.session.execute(sql, {
        "id": id,
        "title": title,
        "author": author,
        "year": year,
        "publisher": publisher,
        "address": address
    })
    db.session.commit()

def delete_book(book_id):
    """Deletes a book entry from the database by its ID"""
    sql = text("DELETE FROM book WHERE id = :book_id")
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
