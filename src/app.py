from flask import flash, jsonify, redirect, render_template, request, abort

from config import app, test_env
from db_helper import reset_db
from repositories.book_repository import create_book, get_books, get_book, update_book, delete_book


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
@app.route("/edit/<int:id>", methods=["GET"])
def edit_page(id):
    book = get_book(id)
    if not book:
        abort(404)
    return render_template("edit.html", book=book)

@app.route("/edit/<int:id>", methods=["POST"])
def edit_book(id):
    update_book(
        id,
        request.form["title"],
        request.form["author"],
        request.form["year"],
        request.form["publisher"],
        request.form["address"]
    )
    return redirect("/citations")

@app.route("/citations/delete/<int:book_id>")
def delete_citation(book_id):
    """Deletes a book citation by its ID"""
    delete_book(book_id)
    return redirect("/citations")


