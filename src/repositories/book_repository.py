# pylint: disable=R0917

from sqlalchemy import text

from config import db
from entities.book import Book


def get_books(title=None, author=None, year=None):
    query = "SELECT id, title, author, year, publisher, address FROM book WHERE 1=1"
    params = {}

    if title:
        query += " AND LOWER(title) LIKE :title"
        params["title"] = f"%{title.lower()}%"

    if author:
        query += " AND LOWER(author) LIKE :author"
        params["author"] = f"%{author.lower()}%"

    if year:
        query += " AND year = :year"
        params["year"] = year

    result = db.session.execute(text(query), params)
    books = result.fetchall()

    return [Book(b[0], b[1], b[2], b[3], b[4], b[5]) for b in books]


def get_book(book_id):
    """Fetches a single book by its ID from the database"""
    sql = text(
        """
        SELECT id, title, author, year, publisher, address
        FROM book WHERE id = :id
    """
    )
    result = db.session.execute(sql, {"id": book_id}).fetchone()
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


def update_book(book_id, title, author, year, publisher, address):  # pylint: disable=too-many-arguments
    sql = text("""
        UPDATE book
        SET title = :title,
            author = :author,
            year = :year,
            publisher = :publisher,
            address = :address
        WHERE id = :id
    """)
    db.session.execute(
        sql,
        {
            "id": book_id,
            "title": title,
            "author": author,
            "year": year,
            "publisher": publisher,
            "address": address,
        },
    )
    db.session.commit()


def delete_book(book_id):
    """Deletes a book entry from the database by its ID"""
    sql = text("DELETE FROM book WHERE id = :book_id")
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
