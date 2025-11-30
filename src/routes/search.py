from flask import render_template, request

from repositories.citation_repository import search_citations
from repositories.entry_type_repository import get_entry_types
from util import parse_search_queries


def get():
    """Renders the search page and handles search queries."""
    queries = parse_search_queries(request.args) or {}

    citations = search_citations(queries)
    entry_types = get_entry_types()

    return render_template(
        "search.html",
        citations=citations,
        entry_types=entry_types
    )
