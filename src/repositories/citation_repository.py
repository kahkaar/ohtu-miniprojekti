from sqlalchemy import text

from config import db
from entities.citation import Citation


def _to_citation(row):
    # pylint: disable=W0511
    # TODO: Move this to utils/equivalent module.
    return Citation(
        row.id,
        row.entry_type,
        row.citation_key,
        row.fields
    )


def get_citations(page=None, per_page=None):
    # N.B. This probably should have a default per_page value...
    """Fetches citations from the database.

    Optional paging:
      - page: 1-based page number
      - per_page: items per page

    If both `page` and `per_page` are provided, the query uses LIMIT/OFFSET
    to return only that page. If omitted, all citations are returned.
    """

    base_sql = (
        """
        SELECT c.id, et.name AS entry_type, c.citation_key, c.fields
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
        ORDER BY c.id
        """
    )

    params = {}
    if isinstance(page, int) and isinstance(per_page, int):
        page = max(page, 1)
        per_page = max(per_page, 1)
        offset = (page - 1) * per_page

        base_sql = base_sql + " LIMIT :limit OFFSET :offset"
        params["limit"] = per_page
        params["offset"] = offset

    sql = text(base_sql)
    result = db.session.execute(sql, params).fetchall()

    if not result:
        return []

    return [_to_citation(c) for c in result]


def get_citation(citation_id):
    """Fetches a citation by its ID from the database"""

    sql = text(
        """
        SELECT c.id, et.name AS entry_type, c.citation_key, c.fields
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
        WHERE c.id = :citation_id
        """
    )

    params = {
        "citation_id": citation_id,
    }

    result = db.session.execute(sql, params).fetchone()

    if not result:
        return None

    return _to_citation(result)


def create_citation(entry_type_id, citation_key, fields):
    """Creates a new citation entry in the database"""

    sql = text(
        """
        INSERT INTO citations (entry_type_id, citation_key, fields)
        VALUES (:entry_type_id, :citation_key, :fields)
        """
    )

    params = {
        "entry_type_id": entry_type_id,
        "citation_key": citation_key,
        "fields": fields,
    }

    db.session.execute(sql, params)
    db.session.commit()


def update_citation(citation_id, entry_type_id=None, citation_key=None, fields=None):
    """Updates an existing citation entry in the database."""

    values = []
    params = {"citation_id": citation_id}

    if entry_type_id:
        values.append("entry_type_id = :entry_type_id")
        params["entry_type_id"] = entry_type_id

    if citation_key:
        values.append("citation_key = :citation_key")
        params["citation_key"] = citation_key

    if fields:
        values.append("fields = :fields")
        params["fields"] = fields

    # Nothing to update; returning.
    # Should this return a value or raise?
    if not values:
        return

    base_sql = (
        f"""
        UPDATE citations
        SET {', '.join(values)}
        WHERE id = :citation_id
        """
    )

    sql = text(base_sql)

    db.session.execute(sql, params)
    db.session.commit()


def delete_citation(citation_id):
    """Deletes a citation entry from the database by its ID"""

    sql = text(
        """
        DELETE FROM citations
        WHERE id = :citation_id
        """
    )

    db.session.execute(sql, {"citation_id": citation_id})
    db.session.commit()

def get_entry_types():
    """
    Returns all entry types from the database as a list of dicts.
    Used for popultaing the dropdown in the filters.
    """

    sql = text("""
        SELECT id, name
        FROM entry_types
        ORDER BY name
    """)

    result = db.session.execute(sql).fetchall()

    return [{"id": row.id, "name": row.name} for row in result]

# pylint: disable=too-many-arguments, too-many-positional-arguments
def search_citations(
    q=None,
    citation_key=None,
    entry_type=None,
    author=None,
    year_from=None,
    year_to=None,
    sort_by=None,
    direction="asc"
):
    filters = []
    params = {}

    sql = """
        SELECT c.id, et.name AS entry_type, c.citation_key, c.fields
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
    """

    if q:
        filters.append("c.fields::text ILIKE :q")
        params["q"] = f"%{q}%"

    if citation_key:
        filters.append("c.citation_key ILIKE :citation_key")
        params["citation_key"] = f"%{citation_key}%"

    if entry_type:
        filters.append("et.name = :entry_type")
        params["entry_type"] = entry_type

    if author:
        filters.append("c.fields->>'author' ILIKE :author")
        params["author"] = f"%{author}%"

    if year_from:
        filters.append("(c.fields->>'year')::int >= :year_from")
        params["year_from"] = int(year_from)

    if year_to:
        filters.append("(c.fields->>'year')::int <= :year_to")
        params["year_to"] = int(year_to)

    if filters:
        sql += " WHERE " + " AND ".join(filters)

    # Sorting
    if sort_by == "year":
        sql += f" ORDER BY (c.fields->>'year')::int {direction}"
    elif sort_by == "citation_key":
        sql += f" ORDER BY c.citation_key {direction}"
    else:
        sql += " ORDER BY c.id ASC"

    result = db.session.execute(text(sql), params).fetchall()
    return [_to_citation(r) for r in result]
