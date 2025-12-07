from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

import util
from repositories.category_repository import (
    get_categories,
    get_or_create_category,
    get_or_create_tags,
    get_tags,
)
from repositories.citation_repository import (
    get_citation_by_id,
    update_citation_with_metadata,
)


def get(citation_id):
    """Renders the edit page for a specific citation by its ID"""
    citation = get_citation_by_id(citation_id)
    categories = get_categories()
    tags = get_tags()

    return render_template(
        "edit.html",
        citation=citation,
        categories=categories,
        tags=tags,
    )


def post(citation_id):
    """Handles the submission of the edit citation form."""
    # pylint: disable=R0801

    citation = get_citation_by_id(citation_id)

    if not citation:
        flash("Citation not found.", "error")
        return redirect(url_for("citations_view"))

    citation_key = util.extract_citation_key(request.form)
    if not citation_key:
        flash("Invalid citation key provided.", "error")
        return redirect(url_for("citations_view"))

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

    year = posted_fields.get("year")
    if year:
        try:
            year_int = int(year)
            if year_int < 0 or year_int > 9999:
                raise ValueError

            posted_fields["year"] = year_int

        except (ValueError, TypeError):
            flash("Year must be a number between 0 and 9999.", "error")
            return redirect(url_for("edit_citation", citation_id=citation_id))
    try:
        update_citation_with_metadata(
            citation_id=citation_id,
            citation_key=citation_key,
            fields=fields,
            category=category,
            tags=tags,
        )
        flash("Citation updated successfully.", "success")
    except (ValueError, TypeError, SQLAlchemyError) as e:
        flash(
            f"An error occurred while updating the citation: {str(e)}", "error")
        return redirect(url_for("citations_view"))

    return redirect(url_for("citations_view", _anchor=f"{citation_id}-{citation_key}"))
