from sqlalchemy import text

from config import db


def get_entry_fields(entry_type_id):
    """Fetches default entry fields for a given entry type ID from the database"""

    sql = text(
        """
        SELECT df.name
        FROM default_entry_fields def
        JOIN default_fields df ON def.default_field_id = df.id
        WHERE def.entry_type_id = :entry_type_id
        ORDER BY df.id
        """
    )

    params = {"entry_type_id": entry_type_id}

    result = db.session.execute(sql, params).fetchall()

    if not result:
        return []

    return sorted([r.name for r in result])
