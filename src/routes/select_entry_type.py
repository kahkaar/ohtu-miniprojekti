from flask import flash, redirect, request, url_for

import util
from repositories.entry_type_repository import get_entry_type


def post():
    """Handles the submission of the entry type selection form."""

    entry_type = request.form.get("entry_type")

    if not entry_type:
        flash("No entry type selected.", "error")
        return redirect(url_for("index"))

    entry_type_obj = get_entry_type(entry_type)
    if not entry_type_obj:
        flash("Entry type was not found.", "error")
        return redirect(url_for("index"))

    flash(f"Selected entry type '{entry_type_obj.name}'", "info")
    util.set_session("entry_type", entry_type_obj.to_dict())

    return redirect(url_for("index"))
