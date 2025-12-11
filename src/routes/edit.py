from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

import util
from errors import CitationNotFoundError
from repositories.category_repository import (
    get_categories,
    get_or_create_metadata,
    get_tags,
)
from repositories.citation_repository import (
    get_citation_by_id,
    update_citation_with_metadata,
    validate_citation,
)
from repositories.entry_fields_repository import get_default_fields
from repositories.entry_type_repository import get_entry_type, get_entry_types


def get(citation_id):
    """Renders the edit page for a specific citation by its ID"""

    entry_types = get_entry_types()
    categories = get_categories()
    tags = get_tags()
    default_fields = get_default_fields()

    try:
        citation = get_citation_by_id(citation_id)
    except CitationNotFoundError:
        citation = None

    return render_template(
        "edit.html",
        citation=citation,
        entry_types=entry_types,
        categories=categories,
        tags=tags,
        default_fields=default_fields,
    )


def post(citation_id):
    """Handles the submission of the edit citation form."""

    entry_type_id = request.form.get("entry_type", "")
    entry_type_id = util.sanitize(entry_type_id)
    entry_type_obj = None
    if entry_type_id:
        if not entry_type_id.isdigit():
            flash("Entry type ID is not numeric.", "error")
            return redirect(url_for("edit_citation", citation_id=citation_id))
        entry_type_obj = get_entry_type(int(entry_type_id))

    try:
        # Methods raise exceptions on failure, so no need to check return values
        validate_citation(citation_id)
        citation_key = util.extract_citation_key(request.form)

        fields, category_names, tag_names = util.extract_data(request.form)
        categories, tags = get_or_create_metadata(category_names, tag_names)

        update_citation_with_metadata(
            citation_id=citation_id,
            citation_key=citation_key,
            fields=fields,
            categories=categories,
            tags=tags,
            entry_type_id=entry_type_obj.id if entry_type_obj else None,
        )

        flash("Citation was updated successfully.", "success")
    except (ValueError, TypeError, SQLAlchemyError, CitationNotFoundError) as e:
        flash(
            f"An error occurred while updating the citation: {str(e)}", "error")
        return redirect(url_for("citations_view"))

    return redirect(url_for("citations_view", _anchor=f"{citation_id}-{citation_key}"))
