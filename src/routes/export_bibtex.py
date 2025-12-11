from flask import Response, request

from repositories.citation_repository import get_citations_by_ids, get_citations_by_keys


def get():
    """Exports selected citations as a .bib file"""

    ids_string = request.args.get("citation_ids", "")
    if ids_string:
        ids = [int(id) for id in ids_string.split(",")]
        citations = get_citations_by_ids(ids)
    else:
        keys_string = request.args.get("citation_keys", "")
        keys = keys_string.split(",")
        citations = get_citations_by_keys(keys)

    bibtex = "\n\n".join(c.to_bibtex() for c in citations)
    bibtex += "\n"

    response = Response(bibtex, mimetype='application/x-bibtex')
    response.headers['Content-Disposition'] = 'attachment; filename=selected_citations.bib'

    return response
