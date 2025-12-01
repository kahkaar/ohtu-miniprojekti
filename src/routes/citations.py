from flask import render_template

from repositories.citation_repository import get_citations


def get():
    """Renders the citations page showing all saved citations."""
    citations = get_citations()
    return render_template("citations.html", citations=citations)
