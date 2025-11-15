from flask import flash, jsonify, redirect, render_template, request

from config import app, test_env
from db_helper import create_book, reset_db
from models import Book
from repositories.todo_repository import create_todo, get_todos, set_done
from util import validate_todo


@app.route("/", methods=["GET", "POST"])
def index():
    """Handles the main page for viewing and adding books"""
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        year = request.form.get("year")
        publisher = request.form.get("publisher")
        address = request.form.get("address")

        if not title or not author:
            return redirect("/")
        else:
            create_book(title, author, year, publisher, address)
            flash("Book added successfully!")
            return redirect("/")

        return redirect("/")

    return render_template("index.html")


# testausta varten oleva reitti
if test_env:
    @app.route("/reset_db")
    def reset_database():
        reset_db()
        return jsonify({'message': "db reset"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
