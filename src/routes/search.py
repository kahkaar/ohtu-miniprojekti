from flask import render_template, request

from repositories.citation_repository import search_citations
from repositories.entry_type_repository import get_entry_types
from repositories.category_repository import get_tags, get_categories
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
    request.args.get("advanced"),
    request.args.getlist("tags"),
    request.args.getlist("categories"),])

    return render_template(
        "citations.html",
        citations=citations,
        entry_types=entry_types,
        tags = get_tags(),
        categories = get_categories(),
        selected_tags=queries.get("tags", []),
        selected_categories=queries.get("categories", []),
        advanced_open=advanced_open
    )
