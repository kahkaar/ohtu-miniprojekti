from flask import jsonify, request

import util


def post():
    """AJAX endpoint: accepts form/json payload with 'doi' and returns metadata or error."""
    doi = None
    if request.is_json:
        doi = request.json.get("doi")
    else:
        doi = request.form.get("doi")

    if not doi:
        return jsonify({"error": "No DOI provided."}), 400

    fields = util.fetch_doi_metadata(doi)
    if not fields:
        return jsonify({"error": "Metadata not found for provided DOI."}), 404

    return jsonify({"fields": fields}), 200
