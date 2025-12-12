from flask import render_template, request

from repositories.category_repository import get_categories, get_tags
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
        request.args.get("advanced"),
        request.args.getlist("tag_list"),
        request.args.getlist("category_list"),
    ])

    selected_tags = queries.get("tag_list", [])
    selected_categories = queries.get("category_list", [])

    return render_template(
        "citations.html",
        citations=citations,
        entry_types=entry_types,
        tags=get_tags(),
        categories=get_categories(),
        selected_tags=selected_tags,
        selected_categories=selected_categories,
        advanced_open=advanced_open
    )
