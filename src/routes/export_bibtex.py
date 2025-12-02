from flask import request, Response

from repositories.citation_repository import get_citation

def get():
    """Exports selected citations as a .bib file"""
    ids_string = request.args.get('citation_ids')
    ids = [int(id) for id in ids_string.split(',')]
    citations = [get_citation(citation_id) for citation_id in ids]
    bibtex = "\n\n".join(citation.to_bibtex() for citation in citations)
    bibtex += "\n"

    response = Response(bibtex)
    response.headers.set('Content-Disposition', 'attachment', filename='selected_citations.bib')
    return response
