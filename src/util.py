import json
import re

import requests
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

    raw_tags = args.getlist("tags")
    tags = [sanitize(t).strip() for t in raw_tags if sanitize(t).strip()]

    raw_categories = args.getlist("categories")
    categories = [sanitize(c).strip() for c in raw_categories if sanitize(c).strip()]

    return {
        "q": q_sanitized or "",
        "citation_key": _str_lower("citation_key"),
        "entry_type": _str_lower("entry_type"),
        "author": _str_lower("author"),
        "year_from": _int_or_none(args.get("year_from")),
        "year_to": _int_or_none(args.get("year_to")),
        "sort_by": sort_by,
        "direction": direction,
        "tags": tags,
        "categories": categories,
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


def _doi_extract(value):
    s = str(value).strip()
    m = re.search(r"10\.\d{4,9}/\S+", s)
    return m.group(0).rstrip(".") if m else None


def _doi_request_json(doi):
    url = "https://citation.doi.org/metadata"
    headers = {
        "Accept": "application/vnd.citationstyles.csl+json, application/json"}
    resp = requests.get(url, params={"doi": doi}, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _doi_first_of_keys(dct, keys):
    for k in keys:
        v = dct.get(k)
        if v:
            if isinstance(v, list):
                return v[0]
            return v
    return None


def _doi_parse_authors(auth_list):
    if not isinstance(auth_list, (list, tuple)):
        return None
    parts = []
    for a in auth_list:
        if isinstance(a, dict):
            given = a.get("given")
            family = a.get("family")
            literal = a.get("literal")
            if given and family:
                parts.append(f"{given} {family}")
            elif literal:
                parts.append(literal)
            elif family:
                parts.append(family)
        elif isinstance(a, str):
            parts.append(a)
    return "; ".join(parts) if parts else None


def _doi_parse_year(dct):
    issued = dct.get("issued") or dct.get("created") or {}
    if not isinstance(issued, dict):
        return None
    dp = issued.get("date-parts") or issued.get("date_parts")
    if isinstance(dp, list) and dp and isinstance(dp[0], (list, tuple)) and dp[0]:
        first = dp[0][0]
        try:
            return int(first)
        except (TypeError, ValueError):
            return None
    return None


def fetch_doi_metadata(doi_input):
    """Fetch citation metadata for a DOI.

    This function extracts a DOI from the input, queries the DOI metadata
    endpoint and returns a compact `fields` dict. It delegates parsing tasks
    to small helpers to keep complexity low (fewer local variables and
    branches) and avoids catching overly broad exceptions.
    """
    # pylint: disable=R0912

    if not doi_input:
        return None

    doi = _doi_extract(doi_input)
    if not doi:
        return None

    try:
        data = _doi_request_json(doi)
    except requests.RequestException:
        return None
    except ValueError:
        return None

    if not isinstance(data, dict):
        return None

    fields = {}

    title = _doi_first_of_keys(data, ("title",))
    if title:
        fields["title"] = title

    author_str = _doi_parse_authors(data.get("author") or data.get("authors"))
    if author_str:
        fields["author"] = author_str

    year_val = _doi_parse_year(data)
    if isinstance(year_val, int) and 0 <= year_val <= 9999:
        fields["year"] = year_val

    journ = _doi_first_of_keys(
        data, ("container-title", "container_title", "journaltitle", "journal"))
    if journ:
        fields["journaltitle"] = journ

    pub = _doi_first_of_keys(data, ("publisher", "publisher-name"))
    if pub:
        fields["publisher"] = pub

    pages = data.get("page") or data.get("pages")
    if pages:
        fields["pages"] = pages

    vol = data.get("volume")
    if vol is not None:
        fields["volume"] = str(vol)

    num = data.get("issue") or data.get("number")
    if num is not None:
        fields["number"] = str(num)

    return fields or None
