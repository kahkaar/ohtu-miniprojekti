from flask import request, Response

from repositories.citation_repository import get_citation_by_id, get_citation_by_key

def get():
    """Exports selected citations as a .bib file"""
    ids_string = request.args.get('citation_ids', '')
    if ids_string:
        ids = [int(id) for id in ids_string.split(',')]
        citations = [get_citation_by_id(citation_id) for citation_id in ids]
    else:
        keys_string = request.args.get('citation_keys', '')
        keys = list(keys_string.split(','))
        citations = [get_citation_by_key(key) for key in keys]
    bibtex = "\n\n".join(citation.to_bibtex() for citation in citations)
    bibtex += "\n"

    response = Response(bibtex, mimetype='application/x-bibtex')
    response.headers.set('Content-Disposition', 'attachment', filename='selected_citations.bib')
    return response
