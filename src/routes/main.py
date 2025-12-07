from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

import util
from repositories.category_repository import (
    get_categories,
    get_or_create_category,
    get_or_create_tags,
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

# pylint: disable=R0911


def post():
    """Handles the submission of the main index form to create a new citation."""
    # pylint: disable=R0801

    # Retrieve the selected entry type from the session, set when selecting entry type.
    entry_type = util.get_session("entry_type")
    entry_type = util.parse_entry_type(entry_type)

    if not entry_type:
        flash("No entry type selected.", "error")
        return redirect(url_for("index"))

    citation_key = util.extract_citation_key(request.form)
    if not citation_key:
        flash("Invalid citation key provided.", "error")
        return redirect(url_for("index"))

    # Extract posted fields. Dynamic extra fields (created by JS) will appear
    # as regular form keys and are picked up by extract_fields.
    fields = util.extract_fields(request.form)
    category_name = util.extract_category(request.form)
    tag_names = util.extract_tags(request.form)

    # Convert names to objects (create if not present)
    category = None
    tags = None
    if category_name:
        category = get_or_create_category(category_name)

    if tag_names:
        tags = get_or_create_tags(tag_names)

    year = fields.get("year")
    if year:
        try:
            year_int = int(year)
            if year_int < 0 or year_int > 9999:
                raise ValueError

            fields["year"] = year_int

        except (ValueError, TypeError):
            flash("Year must be a number between 0 and 9999.", "error")
            return redirect(url_for("index"))

    try:
        create_citation_with_metadata(
            entry_type=entry_type,
            citation_key=citation_key,
            fields=fields,
            category=category,
            tags=tags
        )

        flash("A new citation was added successfully!", "success")
    except (ValueError, TypeError, SQLAlchemyError) as e:
        flash(
            f"An error occurred while adding the citation: {str(e)}", "error")

    return redirect(url_for("index"))
