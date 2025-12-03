from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

import util
from repositories.citation_repository import get_citation, update_citation


def get(citation_id):
    """Renders the edit page for a specific citation by its ID"""
    citation = get_citation(citation_id)
    return render_template("edit.html", citation=citation)


def post(citation_id):
    """Handles the submission of the edit citation form."""
    # pylint: disable=R0801
    citation = get_citation(citation_id)

    if not citation:
        flash("Citation not found.", "error")
        return redirect(url_for("citations_view"))

    citation_key = request.form.get("citation_key", "")

    # Collapsing whitespace for citation key only, since it should not contain any spaces.
    sanitized_citation_key = util.collapse_whitespace(citation_key)
    if not sanitized_citation_key:
        flash("Invalid citation key provided.", "error")
        return redirect(url_for("citations_view"))

    posted_fields = util.get_posted_fields(request.form)
    # Maybe add a check here to see if fields have actually changed.

    if not posted_fields:
        flash("No fields provided for the citation.", "error")
        return redirect(url_for("index"))

    year = posted_fields.get("year")
    if year:
        try:
            year_int = int(year)
            if year_int < 0 or year_int > 9999:
                raise ValueError

            posted_fields["year"] = year_int

        except (ValueError, TypeError):
            flash("Year must be a number between 0 and 9999.", "error")
            return redirect(url_for("index"))
    try:
        update_citation(
            citation_id=citation_id,
            citation_key=sanitized_citation_key,
            fields=posted_fields
        )
        flash("Citation updated successfully.", "success")
    except (ValueError, TypeError, SQLAlchemyError) as e:
        flash(
            f"An error occurred while updating the citation: {str(e)}", "error")
        return redirect(url_for("citations_view"))

    return redirect(url_for("citations_view", _anchor=f"{citation_id}-{sanitized_citation_key}"))
