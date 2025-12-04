from flask import redirect, request, url_for

import routes.bibtex
import routes.citations
import routes.delete
import routes.edit
import routes.main
import routes.search
import routes.select_entry_type
import routes.testing_env
import routes.export_bibtex
from config import app, test_env

if test_env:
    @app.route("/test_env/reset_db")
    def reset_database():
        return routes.testing_env.reset_database()

    @app.route("/test_env/db_tables")
    def db_tables():
        return routes.testing_env.db_tables()

    @app.route("/test_env/session")
    def session_data():
        return routes.testing_env.session_data()

    @app.route("/test_env/citations")
    def json_citations():
        return routes.testing_env.json_citations()


@app.route("/", methods=["GET", "POST"])
def index():
    """Renders the index page and handles new citation submissions."""
    if request.method == "POST":
        return routes.main.post()
    return routes.main.get()


@app.route("/select_entry_type", methods=["POST"])
def select_entry_type():
    """Handles the selection of an entry type."""
    return routes.select_entry_type.post()


@app.route("/citations", methods=["GET"])
def citations_view():
    """Renders the citations page showing all saved citations."""
    return routes.citations.get()


@app.route("/edit/<int:citation_id>", methods=["GET", "POST"])
def edit_citation(citation_id):
    """Renders the edit page for a specific citation by its ID"""
    if request.method == "POST":
        return routes.edit.post(citation_id)
    return routes.edit.get(citation_id)


@app.route("/delete/<int:citation_id>", methods=["POST"])
def delete_citation(citation_id):
    """Deletes a citation by its ID"""
    return routes.delete.post(citation_id)


@app.route("/bibtex/<int:citation_id>", methods=["GET"])
def show_bibtex(citation_id):
    """Renders the bibtex page for a specific citation by its ID"""
    return routes.bibtex.get(citation_id)


@app.route("/export_bibtex", methods=["GET"])
def export_bibtex():
    """Exports selected citations as a .bib file"""
    return routes.export_bibtex.get()


@app.route("/search", methods=["GET"])
@app.route("/citations/search", methods=["GET"])
def citations_search():
    """Renders the search page and handles search queries."""
    return routes.search.get()


@app.route("/edit")
@app.route("/delete")
@app.route("/bibtex")
def redirect_to_citations():
    """Redirects to the citations page if no citation ID is provided."""
    return redirect(url_for("citations_view"))
