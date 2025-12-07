from flask import render_template, request

from repositories.citation_repository import search_citations
from repositories.entry_type_repository import get_entry_types
from util import parse_search_queries


def get():
    queries = parse_search_queries(request.args) or {}
    citations = search_citations(queries)
    entry_types = get_entry_types()
    advanced_open = any([
    request.args.get("entry_type"),
    request.args.get("citation_key"),
    request.args.get("author"),
    request.args.get("year_from"),
    request.args.get("year_to"),
    request.args.get("advanced"),])

    return render_template(
        "search.html",
        citations=citations,
        entry_types=entry_types,
        advanced_open=advanced_open)
