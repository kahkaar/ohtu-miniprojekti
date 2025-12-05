from flask import jsonify, redirect, session, url_for
from sqlalchemy import text

from config import test_env
from db_helper import db, reset_db, tables
from repositories.category_repository import get_categories, get_tags
from repositories.citation_repository import get_citations


def _check_test_env():
    """Helper to validate testing environment. Must be used only in testing routes."""
    if not test_env:
        return redirect(url_for("index"))
    return None


def reset_database():
    """Resets the database to its initial data."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    reset_db()
    return jsonify({"message": "Database was reset with initial data."})


def db_tables():
    """Returns a list of database tables."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    table_list = tables()
    return jsonify({"tables": table_list})


def session_data():
    """Returns the current session data."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    return jsonify(dict(session))


def json_citations():
    """Returns all citations in JSON format."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    citations = get_citations()
    return jsonify([citation.to_dict() if citation else {} for citation in citations])


def json_tags():
    """Returns all tags in JSON format."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    tags = get_tags()
    return jsonify([tag.to_dict() if tag else {} for tag in tags])


def json_categories():
    """Returns all categories in JSON format."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    categories = get_categories()
    return jsonify([category.to_dict() if category else {} for category in categories])


def json_citations_to_categories():
    """Returns all citations to categories mappings in JSON format."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    result = db.session.execute(
        text("SELECT * FROM citations_to_categories")).fetchall()
    mappings = [
        {"citation_id": row.citation_id, "category_id": row.category_id}
        for row in result
    ]
    return jsonify(mappings)


def json_citations_to_tags():
    """Returns all citations to tags mappings in JSON format."""
    not_test_env = _check_test_env()
    if not_test_env:
        return not_test_env

    result = db.session.execute(
        text("SELECT * FROM citations_to_tags")).fetchall()
    mappings = [
        {"citation_id": row.citation_id, "tag_id": row.tag_id}
        for row in result
    ]
    return jsonify(mappings)
