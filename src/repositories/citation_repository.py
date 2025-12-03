import json

from sqlalchemy import text

from config import db
from entities.citation import Citation


def _to_citation(row):
    """Converts a database row to a Citation object."""
    if not row:
        return None

    fields = row.fields or ""
    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except json.JSONDecodeError:
            fields = {}

    return Citation(
        row.id,
        row.entry_type,
        row.citation_key,
        fields
    )


def get_citations(page=None, per_page=None):
    """Fetches citations from the database.

    Optional paging:
      - page: 1-based page number
      - per_page: items per page

    If both `page` and `per_page` are provided, the query uses LIMIT/OFFSET
    to return only that page. If omitted, all citations are returned.
    """
    # N.B. This method should probably have a default per_page value...
    base_sql = (
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key, c.fields
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


def get_citation_by_id(citation_id):
    """Fetches a citation by its ID from the database"""

    sql = text(
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key, c.fields
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
        WHERE c.id = :citation_id
        ORDER BY et.name
        """
    )

    params = {
        "citation_id": citation_id,
    }

    result = db.session.execute(sql, params).fetchone()

    if not result:
        return None

    return _to_citation(result)

def get_citation_by_key(citation_key):
    """Fetches a citation by its citation key from the database"""

    sql = text(
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key, c.fields
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
        WHERE c.citation_key = :citation_key
        ORDER BY et.name
        """
    )

    params = {
        "citation_key": citation_key,
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

    serialized = json.dumps(fields or {})

    params = {
        "entry_type_id": entry_type_id,
        "citation_key": citation_key,
        "fields": serialized,
    }
    try:
        db.session.execute(sql, params)
        db.session.commit()

    except Exception as exc:

        raise ValueError(f"Citation key '{citation_key}' already exists.") from exc


def update_citation(
        citation_id,
        entry_type_id=None,
        citation_key=None,
        fields=None
):
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
        serialized = json.dumps(fields or {})
        values.append("fields = :fields")
        params["fields"] = serialized

    # Nothing to update; returning.
    # Should this return a value or raise?
    if not values:
        return

    base_sql = (
        f"""
        UPDATE citations
        SET {", ".join(values)}
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


def search_citations(queries=None):
    if queries is None:
        queries = {}
    base_sql = """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
    """

    def _to_int(v):
        if v is None or v == "":
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    year_from = _to_int(queries.get("year_from"))
    year_to = _to_int(queries.get("year_to"))

    filters = []
    params = {}

    if queries.get("q"):
        filters.append("c.fields::text ILIKE :q")
        params["q"] = f"%{queries.get('q')}%"

    if queries.get("citation_key"):
        filters.append("c.citation_key ILIKE :citation_key")
        params["citation_key"] = f"%{queries.get('citation_key')}%"

    if queries.get("entry_type"):
        filters.append("et.name = :entry_type")
        params["entry_type"] = queries.get('entry_type')

    if queries.get("author"):
        filters.append("c.fields->>'author' ILIKE :author")
        params["author"] = f"%{queries.get('author')}%"

    if year_from:
        filters.append("(c.fields->>'year')::int >= :year_from")
        params["year_from"] = year_from

    if year_to:
        filters.append("(c.fields->>'year')::int <= :year_to")
        params["year_to"] = year_to

    if filters:
        base_sql += " WHERE " + " AND ".join(filters)

    allowed_sort_by = {"year", "citation_key"}
    allowed_direction = {"ASC", "DESC"}
    sort_by = (queries.get("sort_by") or "").lower()
    direction = (queries.get("direction") or "ASC").upper()

    sort_by = sort_by if sort_by in allowed_sort_by else None
    direction = direction if direction in allowed_direction else "ASC"

    if sort_by == "year":
        base_sql += f" ORDER BY (c.fields->>'year')::int {direction}"
    elif sort_by == "citation_key":
        base_sql += f" ORDER BY c.citation_key {direction}"
    else:
        base_sql += " ORDER BY c.id ASC"

    sql = text(base_sql)

    result = db.session.execute(sql, params).fetchall()
    return [_to_citation(r) for r in result]
