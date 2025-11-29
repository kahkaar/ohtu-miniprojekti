from flask import jsonify, redirect, session, url_for

from config import test_env
from db_helper import reset_db, tables
from repositories.citation_repository import get_citations


def _ensure_test_env():
    # Ensurance that this route is only available in test environment.
    if not test_env:
        return redirect(url_for("index"))
    return None


def reset_database():
    """Resets the database to its initial data."""
    ensurance = _ensure_test_env()
    if ensurance:
        return ensurance

    reset_db()
    return jsonify({"message": "Database was reset with initial data."})


def db_tables():
    """Returns a list of database tables."""
    ensurance = _ensure_test_env()
    if ensurance:
        return ensurance

    table_list = tables()
    return jsonify({"tables": table_list})


def session_data():
    """Returns the current session data."""
    ensurance = _ensure_test_env()
    if ensurance:
        return ensurance

    return jsonify(dict(session))


def json_citations():
    """Returns all citations in JSON format."""
    ensurance = _ensure_test_env()
    if ensurance:
        return ensurance

    citations = get_citations()
    return jsonify([citation.to_dict() for citation in citations])
