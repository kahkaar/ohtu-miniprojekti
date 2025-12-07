import json

from flask import session

from entities.category import Category, Tag
from entities.citation import Citation
from entities.entry_type import EntryType


def sanitize(value):
    """
    Sanitizes user input by stripping leading/trailing whitespace
    and collapsing internal whitespace.
    """
    if isinstance(value, str):
        return " ".join(value.strip().split())
    return value


def validate(value):
    """Validates that the input value is a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def collapse_whitespace(value):
    """
    Collapses any whitespace characters into nothing.
    Used for certain identifiers.
    """
    if isinstance(value, str):
        return "".join(value.strip().split())
    return value


def collapse_to_hyphens(value):
    """
    Replaces spaces with hyphens.
    Used for certain identifiers.
    """
    if isinstance(value, str):
        return "-".join(value.strip().split())
    return value


def extract_fields(form):
    """Extracts and sanitizes posted fields from a form."""

    disallowed_keys = {
        "citation_key",
        "entry_type",
        "category",
        "category_new",
        "tags",
        "tags_new",
    }

    fields = {}
    for k, v in form.items():
        # Citation key and entry type are handled separately.
        if k in disallowed_keys:
            continue

        sanitized_value = sanitize(v)
        if validate(sanitized_value):
            fields[k] = sanitized_value

    return fields


def set_session(key, value):
    """Sets a value in the session."""
    session[key] = value


def get_session(key, default=None):
    """Retrieves a value from the session."""
    return session.get(key, default)


def parse_entry_type(entry_type_data):
    """Parses entry type data from session into an EntryType object."""
    if not entry_type_data:
        return None
    return EntryType(entry_type_data.get("id"), entry_type_data.get("name"))


def clear_session(key=None):
    """Clears a value from the session, or the entire session if no key is provided."""
    if not key:
        return session.clear()
    session.pop(key, None)
    return None


def parse_search_queries(args):
    """Parse and normalize search query parameters from a request args mapping.

    Normalizations applied:
    - trims/collapses whitespace for string inputs
    - lowercases `citation_key`, `entry_type`, `author`, `sort_by`
    - uppercases `direction` and validates it to either 'ASC' or 'DESC'
    - parses `year_from` and `year_to` to ints when possible, otherwise None
    - restricts `sort_by` to a small whitelist (None if not allowed)

    Returns a dict with the same keys the rest of the app expects.
    """
    def _int_or_none(value):
        try:
            if not value or not str(value).isdigit():
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    def _str_lower(name):
        v = args.get(name, "")
        if v is None:
            v = ""
        s = sanitize(v)
        return s.lower() if isinstance(s, str) else ""

    allowed_sort_by = {"year", "citation_key"}

    sort_by = _str_lower("sort_by")
    if sort_by not in allowed_sort_by:
        sort_by = None

    direction = sanitize(args.get("direction", "ASC")).upper()
    if direction not in ("ASC", "DESC"):
        direction = "ASC"

    q_val = args.get("q", "")
    q_sanitized = sanitize(q_val) if q_val is not None else ""

    return {
        "q": q_sanitized or "",
        "citation_key": _str_lower("citation_key"),
        "entry_type": _str_lower("entry_type"),
        "author": _str_lower("author"),
        "year_from": _int_or_none(args.get("year_from")),
        "year_to": _int_or_none(args.get("year_to")),
        "sort_by": sort_by,
        "direction": direction,
    }


def extract_category(form):
    """Extracts and creates the category from the request form data if needed."""

    new_category = form.get("category_new")
    if new_category:
        sanitized = sanitize(new_category)
        if sanitized:
            return sanitized

    # Category can have spaces, so just sanitize.
    category = form.get("category")
    sanitized = sanitize(category)
    if not sanitized:
        return None

    return sanitized


def extract_tags(form):
    """Extracts and creates the tags from the request form data if needed."""

    tag_form_list = form.getlist("tags") or []
    sanitized = []
    for tag_name in tag_form_list:
        # Tags can have spaces, so just sanitize.
        tag = sanitize(tag_name)
        if tag:
            sanitized.append(tag)

    tags_new = form.get("tags_new")
    if tags_new:
        parts = [sanitize(p) for p in tags_new.split(",")]
        for p in parts:
            if p:
                sanitized.append(p)

    seen = set()
    unique = []
    for t in sanitized:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique


def extract_citation_key(form):
    """Extracts the citation key from the request form data."""
    citation_key = form.get("citation_key", "")

    # Citation keys cannot have spaces, so sanitize and collapse to hyphens.
    sanitized = sanitize(citation_key)
    collapsed = collapse_to_hyphens(sanitized)
    if not collapsed:
        return None

    return collapsed


def to_category(row):
    """Converts a database row to a Category object."""
    return Category(
        category_id=row.id,
        name=row.name,
    )


def to_tag(row):
    """Converts a database row to a Tag object."""
    return Tag(
        tag_id=row.id,
        name=row.name,
    )


def to_citation(row):
    """Converts a database row to a Citation object."""
    if not row:
        return None

    def _parse_fields(val):
        if not val:
            return {}
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return {}
        return val

    def _to_list(val):
        if not val:
            return []
        if isinstance(val, (list, tuple)):
            return list(val)
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                return list(parsed)
            except json.JSONDecodeError:
                pass
            return [p.strip() for p in val.split(",") if p.strip()]
        try:
            return list(val)
        except TypeError:
            return []

    fields = _parse_fields(row.fields)
    tags = _to_list(getattr(row, "tags", None))
    categories = _to_list(getattr(row, "categories", None))

    return Citation(
        row.id,
        row.entry_type,
        row.citation_key,
        fields,
        metadata={"tags": tags, "categories": categories},
    )


def to_entry_type(row):
    """Converts a database row to an EntryType object."""
    return EntryType(
        entry_type_id=row.id,
        name=row.name,
    )
