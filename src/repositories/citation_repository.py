import json

from sqlalchemy import text

from config import db
from errors import CitationNotFoundError
from repositories.category_repository import (
    assign_categories_to_citation,
    assign_metadata_to_citation,
    assign_tags_to_citation,
)
from util import to_citation


def get_citations(page=None, per_page=None):
    """Fetches all citations from the database, with optional pagination."""

    base_sql = (
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = c.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = c.id
            ), ARRAY[]::text[]) AS categories
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

    return [to_citation(c) for c in result]


def validate_citation(citation_id):
    """Validates that a citation with the given ID exists."""
    citation = get_citation_by_id(citation_id)
    if not citation:
        raise CitationNotFoundError("Citation not found.")


def get_citation_by_id(citation_id):
    """Fetches a citation by its ID from the database"""

    sql = text(
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = c.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = c.id
            ), ARRAY[]::text[]) AS categories
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
        raise CitationNotFoundError("Citation not found.")

    return to_citation(result)


def get_citations_by_ids(citation_ids):
    """Fetches multiple citations by their IDs from the database"""

    if not citation_ids:
        return []

    sql = text(
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = c.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = c.id
            ), ARRAY[]::text[]) AS categories
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
        WHERE c.id IN :citation_ids
        ORDER BY et.name
        """
    )

    params = {
        "citation_ids": tuple(citation_ids),
    }

    result = db.session.execute(sql, params).fetchall()

    if not result:
        return []

    values = []
    for r in result:
        if not r:
            continue
        values.append(to_citation(r))

    return values


def get_citation_by_key(citation_key):
    """Fetches a citation by its citation key from the database"""

    sql = text(
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = c.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = c.id
            ), ARRAY[]::text[]) AS categories
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

    return to_citation(result)


def get_citations_by_keys(citation_keys):
    """Fetches multiple citations by their citation keys from the database"""

    if not citation_keys:
        return []

    sql = text(
        """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = c.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = c.id
            ), ARRAY[]::text[]) AS categories
        FROM citations c
        JOIN entry_types et ON c.entry_type_id = et.id
        WHERE c.citation_key IN :citation_keys
        ORDER BY et.name
        """
    )

    params = {
        "citation_keys": tuple(citation_keys),
    }

    result = db.session.execute(sql, params).fetchall()

    if not result:
        return []

    values = []
    for r in result:
        if not r:
            continue
        values.append(to_citation(r))

    return values


def create_citation(entry_type_id, citation_key, fields):
    """Creates a new citation entry in the database."""

    sql = text(
        """
        WITH inserted AS (
            INSERT INTO citations (entry_type_id, citation_key, fields)
            VALUES (:entry_type_id, :citation_key, :fields)
            RETURNING id, entry_type_id, citation_key, fields
        )
        SELECT
            i.id,
            et.name AS entry_type,
            i.citation_key,
            i.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = i.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = i.id
            ), ARRAY[]::text[]) AS categories
        FROM inserted i
        JOIN entry_types et ON i.entry_type_id = et.id
        """
    )

    serialized = json.dumps(fields or {})

    params = {
        "entry_type_id": entry_type_id,
        "citation_key": citation_key,
        "fields": serialized,
    }

    result = db.session.execute(sql, params).fetchone()
    db.session.commit()

    if not result:
        return None

    return to_citation(result)


def create_citation_with_metadata(
        entry_type,
        citation_key,
        fields,
        categories=None,
        tags=None
):
    """Creates a new citation along with its associated categories and tags."""

    existing = get_citation_by_key(citation_key)
    if existing:
        raise ValueError(f"Citation key '{citation_key}' already exists.")

    citation = create_citation(
        entry_type_id=entry_type.id,
        citation_key=citation_key,
        fields=fields
    )

    if not citation:
        raise ValueError("Failed to create citation.")

    assign_metadata_to_citation(citation.id, categories, tags)

    return citation


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


def update_citation_with_metadata(
    citation_id,
    citation_key=None,
    fields=None,
    categories=None,
    tags=None,
    entry_type_id=None,
):  # pylint: disable=R0913,R0917
    """Updates a citation along with its associated categories and tags."""

    update_args = {
        "citation_id": citation_id,
        "citation_key": citation_key,
        "fields": fields,
    }
    if entry_type_id is not None:
        update_args["entry_type_id"] = entry_type_id

    update_citation(**update_args)

    if isinstance(categories, list):
        db.session.execute(
            text(
                """
                DELETE FROM citations_to_categories
                WHERE citation_id = :citation_id
                """
            ),
            {"citation_id": citation_id}
        )
        assign_categories_to_citation(citation_id, categories)

    if isinstance(tags, list):
        db.session.execute(
            text(
                """DELETE FROM citations_to_tags
                WHERE citation_id = :citation_id
                """
            ),
            {"citation_id": citation_id}
        )

        assign_tags_to_citation(citation_id, tags)


def delete_citation(citation_id):
    """Deletes a citation by its ID and cleans up orphaned categories and tags."""

    if not citation_id:
        return

    cat_rows = db.session.execute(
        text(
            """
            SELECT category_id
            FROM citations_to_categories
            WHERE citation_id = :citation_id
            """
        ),
        {"citation_id": citation_id},
    ).fetchall()
    cat_ids = [r[0] for r in cat_rows] if cat_rows else []

    tag_rows = db.session.execute(
        text(
            """
            SELECT tag_id
            FROM citations_to_tags
            WHERE citation_id = :citation_id
            """
        ),
        {"citation_id": citation_id},
    ).fetchall()
    tag_ids = [r[0] for r in tag_rows] if tag_rows else []

    db.session.execute(
        text(
            """
            DELETE FROM citations_to_categories
            WHERE citation_id = :citation_id
            """
        ),
        {"citation_id": citation_id},
    )

    db.session.execute(
        text(
            """
            DELETE FROM citations_to_tags
            WHERE citation_id = :citation_id
            """
        ),
        {"citation_id": citation_id},
    )

    db.session.execute(
        text(
            """
            DELETE FROM citations
            WHERE id = :citation_id
            """
        ),
        {"citation_id": citation_id}
    )

    for cat_id in cat_ids:
        db.session.execute(
            text(
                """
                DELETE FROM categories c
                WHERE c.id = :category_id
                  AND NOT EXISTS (
                      SELECT 1 FROM citations_to_categories ctc
                      WHERE ctc.category_id = c.id
                  )
                """
            ),
            {"category_id": cat_id},
        )

    for tag_id in tag_ids:
        db.session.execute(
            text(
                """
                DELETE FROM tags t
                WHERE t.id = :tag_id
                  AND NOT EXISTS (
                      SELECT 1 FROM citations_to_tags ctt
                      WHERE ctt.tag_id = t.id
                  )
                """
            ),
            {"tag_id": tag_id},
        )

    db.session.commit()


def search_citations(queries=None):
    # pylint: disable=too-many-branches, too-many-statements
    if queries is None:
        queries = {}
    base_sql = """
        SELECT
            c.id,
            et.name AS entry_type,
            c.citation_key,
            c.fields,
            COALESCE((
                SELECT array_agg(t2.name)
                FROM citations_to_tags ctt2
                JOIN tags t2 ON t2.id = ctt2.tag_id
                WHERE ctt2.citation_id = c.id
            ), ARRAY[]::text[]) AS tags,
            COALESCE((
                SELECT array_agg(cat2.name)
                FROM citations_to_categories ctc2
                JOIN categories cat2 ON cat2.id = ctc2.category_id
                WHERE ctc2.citation_id = c.id
            ), ARRAY[]::text[]) AS categories
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

    tag_names = queries.get("tags")
    if tag_names:
        filters.append("""
            c.id IN (
                SELECT citation_id
                FROM citations_to_tags ctt
                JOIN tags t ON t.id = ctt.tag_id
                WHERE t.name = ANY(:tag_names)
            )
        """)
        params["tag_names"] = tag_names

    category_names = queries.get("categories")
    if category_names:
        filters.append("""
            c.id IN (
                SELECT citation_id
                FROM citations_to_categories ctc
                JOIN categories cat ON cat.id = ctc.category_id
                WHERE cat.name = ANY(:category_names)
            )
        """)
        params["category_names"] = category_names

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
    return [to_citation(r) for r in result]
