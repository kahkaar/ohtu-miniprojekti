from flask import session


def sanitize(value):
    """
    Sanitizes user input by stripping leading/trailing
    whitespace and collapsing internal whitespace.
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


def get_posted_fields(form):
    """Extracts and sanitizes posted fields from a form."""
    posted_fields = {}
    for k, v in form.items():
        if k in ("citation_key", "entry_type"):
            continue

        sanitized_value = sanitize(v)
        if validate(sanitized_value):
            posted_fields[k] = sanitized_value

    return posted_fields


def set_session(key, value):
    """Sets a value in the session."""
    session[key] = value


def get_session(key, default=None):
    """Retrieves a value from the session."""
    return session.get(key, default)


def clear_session(key=None):
    """Clears a value from the session."""
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
