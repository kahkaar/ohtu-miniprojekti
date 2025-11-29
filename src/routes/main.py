from flask import flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

import util
from repositories.citation_repository import create_citation
from repositories.entry_fields_repository import get_entry_fields
from repositories.entry_type_repository import get_entry_type, get_entry_types


def get():
    """Renders the main index page."""
    entry_types = get_entry_types()
    entry_fields = []

    selected_entry_type = util.get_session("entry_type")
    if selected_entry_type:
        entry_fields = get_entry_fields(selected_entry_type.get("id"))

    return render_template("index.html", entry_types=entry_types, fields=entry_fields)


def post():
    """Handles the submission of the main index form to create a new citation."""
    # pylint: disable=R0801
    entry_type = request.form.get("entry_type")

    # Exit early if just changing the entry type
    if entry_type:
        entry_type_obj = get_entry_type(entry_type)
        if not entry_type_obj:
            flash("Entry type was not found.", "error")
            return redirect(url_for("index"))

        flash(f"Selected entry type '{entry_type_obj.name}'", "info")
        if entry_type_obj:
            util.set_session("entry_type", entry_type_obj.to_dict())

        return redirect(url_for("index"))

    entry_type = session.get("entry_type")
    if not entry_type:
        flash("No entry type selected.", "error")
        return redirect(url_for("index"))

    citation_key = request.form.get("citation_key", "")

    # Collapsing whitespace for citation key only, since it should not contain any spaces.
    citation_key = util.collapse_whitespace(citation_key)
    if not citation_key:
        flash("Invalid citation key provided.", "error")
        return redirect(url_for("index"))

    sanitized_citation_key = util.sanitize(citation_key)
    posted_fields = util.get_posted_fields(request.form)

    if not posted_fields:
        flash("No fields provided for the citation.", "error")
        return redirect(url_for("index"))

    try:
        create_citation(entry_type.get("id"),
                        sanitized_citation_key, posted_fields)
        flash("A new citation was added successfully!", "success")
    except (ValueError, TypeError, SQLAlchemyError) as e:
        flash(
            f"An error occurred while adding the citation: {str(e)}", "error")

    return redirect(url_for("index"))
