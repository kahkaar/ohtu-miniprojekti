from flask import abort, flash, jsonify, redirect, render_template, request
from repositories.citation_repository import search_citations
from config import app, test_env
from db_helper import reset_db
from util import make_bibtex
from repositories.book_repository import (
    create_book,
    delete_book,
    get_book,
    get_books,
    update_book,
)



@app.route("/", methods=["GET", "POST"])
def index():
    """Handles the main page for viewing and adding books"""
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        year = request.form.get("year")
        publisher = request.form.get("publisher")
        address = request.form.get("address")

        if not title or not author:
            return redirect("/")
        create_book(title, author, year, publisher, address)
        flash("Book added successfully!")
        return redirect("/")

    # Here to not make pylance complain
    abort(405)


# testausta varten oleva reitti
if test_env:
    @app.route("/reset_db")
    def reset_database():
        reset_db()
        return jsonify({'message': "db reset"})


@app.route("/citations")
def citations():
    books = get_books()
    return render_template("citations.html", books=books)


@app.route("/edit/<int:book_id>", methods=["GET"])
def edit_page(book_id):
    book = get_book(book_id)
    if not book:
        abort(404)
    return render_template("edit.html", book=book)


@app.route("/edit/<int:book_id>", methods=["POST"])
def edit_book(book_id):
    title = request.form.get("title")
    author = request.form.get("author")
    year = request.form.get("year")
    publisher = request.form.get("publisher")
    address = request.form.get("address")

    if not title or not author:
        return redirect(f"/edit/{book_id}")
    update_book(
        book_id,
        title,
        author,
        year,
        publisher,
        address
    )
    return redirect("/citations")


@app.route("/bibtex/<int:book_id>", methods=["GET"])
def view_bibtex(book_id):
    """Renders the bibtex view for a specific book by its ID"""
    book = get_book(book_id)
    if not book:
        abort(404)
    bibtex = make_bibtex(book)
    return render_template("bibtex.html", bibtex=bibtex)


@app.route("/citations/delete/<int:book_id>", methods=["GET", "POST"])
def delete_citation(book_id):
    """Deletes a book citation by its ID (supports GET for tests and POST from forms)"""
    delete_book(book_id)
    return redirect("/citations")

@app.route("/citations/search")
def citations_search():
    q = request.args.get("q")
    citation_key = request.args.get("citation_key")
    entry_type = request.args.get("entry_type")

    citations = search_citations(
        q=q,
        citation_key=citation_key,
        entry_type=entry_type
    )

    return render_template("search.html", citations=citations)