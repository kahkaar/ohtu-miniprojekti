from flask import flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from repositories.citation_repository import delete_citation


def post(citation_id):
    """Handles the deletion of a specific citation by its ID"""
    # pylint: disable=R0801
    try:
        delete_citation(citation_id)
        flash("Citation deleted successfully.", "success")
    except (ValueError, TypeError, SQLAlchemyError) as e:
        flash(
            f"An error occurred while deleting the citation: {str(e)}", "error")
    return redirect(url_for("citations_view"))
