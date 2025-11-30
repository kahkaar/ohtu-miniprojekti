from flask import render_template

from repositories.citation_repository import get_citation


def get(citation_id):
    """Renders the BibTeX page for a specific citation by its ID"""
    citation = get_citation(citation_id)
    return render_template("bibtex.html", citation=citation)
