from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

import util
from repositories.category_repository import (
    get_categories,
    get_or_create_metadata,
    get_tags,
)
from repositories.citation_repository import create_citation_with_metadata
from repositories.entry_fields_repository import get_default_fields, get_entry_fields
from repositories.entry_type_repository import get_entry_types


def get():
    """Renders the main index page."""
    entry_types = get_entry_types()
    entry_fields = []

    entry_type = util.get_session("entry_type")
    entry_type = util.parse_entry_type(entry_type)

    if entry_type:
        entry_fields = get_entry_fields(entry_type.id)

    categories = get_categories()
    tags = get_tags()
    default_fields = get_default_fields()

    return render_template(
        "index.html",
        entry_types=entry_types,
        fields=entry_fields,
        categories=categories,
        tags=tags,
        default_fields=default_fields,
    )


def post():
    """Handles the submission of the main index form to create a new citation."""

    entry_type = util.get_session("entry_type")
    entry_type = util.parse_entry_type(entry_type)

    if not entry_type:
        flash("No entry type selected.", "error")
        return redirect(url_for("index"))

    try:
        # Methods raise exceptions on failure, so no need to check return values
        citation_key = util.extract_citation_key(request.form)

        fields, category_names, tag_names = util.extract_data(request.form)
        categories, tags = get_or_create_metadata(category_names, tag_names)

        create_citation_with_metadata(
            entry_type=entry_type,
            citation_key=citation_key,
            fields=fields,
            categories=categories,
            tags=tags
        )

        flash("A new citation was added successfully!", "success")
    except (ValueError, TypeError, SQLAlchemyError) as e:
        flash(
            f"An error occurred while adding the citation: {str(e)}", "error")

    return redirect(url_for("index"))
