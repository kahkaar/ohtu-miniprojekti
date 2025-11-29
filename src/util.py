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
    """Validates user input; raises UserInputError if invalid."""
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
