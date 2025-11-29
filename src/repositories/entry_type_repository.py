from sqlalchemy import text

from config import db
from entities.entry_type import EntryType


def _to_entry_type(row):
    return EntryType(
        row.id,
        row.name,
    )


def get_entry_types():
    """Fetches all entry types from the database"""

    sql = text(
        """
        SELECT id, name
        FROM entry_types
        ORDER BY name, id
        """
    )

    result = db.session.execute(sql).fetchall()

    if not result:
        return []

    return [_to_entry_type(row) for row in result]


def get_entry_type(entry_type_id):
    """Fetches an entry type by its ID from the database"""

    sql = text(
        """
        SELECT id, name
        FROM entry_types
        WHERE id = :entry_type_id
        """
    )

    params = {
        "entry_type_id": entry_type_id,
    }

    result = db.session.execute(sql, params).fetchone()

    if not result:
        return None

    return _to_entry_type(result)


def get_entry_type_by_name(entry_type):
    """Fetches an entry type by its name from the database"""

    sql = text(
        """
        SELECT id, name
        FROM entry_types
        WHERE name = :entry_type
        """
    )

    params = {
        "entry_type": entry_type,
    }

    result = db.session.execute(sql, params).fetchone()

    if not result:
        return None

    return _to_entry_type(result)
