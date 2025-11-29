import os
import re

from sqlalchemy import text

from config import app, db

_IDENTIFIER_RE = re.compile(r"^\w*$")


def _validate_identifier(name):
    """Return the identifier if it is safe, otherwise raise ValueError."""
    if not isinstance(name, str) or not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


def reset_db():
    """
    Clears all contents from all tables in the database.
    Then initializes the database with initial data.
    Used mainly for tests.
    """
    print("\nClearing contents from all tables")

    tables_in_db = tables()
    if not tables_in_db:
        print("No tables found; creating schema and initializing data")
        setup_db()
        init_db()
        return

    for table in tables_in_db:
        safe_table = _validate_identifier(table)
        sql = text(f"TRUNCATE TABLE {safe_table} CASCADE")
        db.session.execute(sql)
    db.session.commit()

    print(f"Cleared database contents. Tables: {", ".join(tables_in_db)}")

    init_db()


def tables():
    """Returns all table names from the database except those ending with _id_seq."""
    sql = text(
        "SELECT table_name "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public' "
        "AND table_name NOT LIKE '%_id_seq'"
    )

    result = db.session.execute(sql).fetchall()
    db.session.commit()
    return [row[0] for row in result]


def setup_db():
    """
    Creating the database.
    Database tables are dropped if they already exist before the creation.
    """
    print("Creating database")

    # Drop existing tables. schema.sql should have drop table if exists as well.
    tables_in_db = tables()
    if tables_in_db:
        print(f"Tables exist, dropping: {", ".join(tables_in_db)}")
        for table in tables_in_db:
            safe_table = _validate_identifier(table)
            sql = text(f"DROP TABLE IF EXISTS {safe_table} CASCADE")
            db.session.execute(sql)
        db.session.commit()

    # Read schema from schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")

    if not os.path.exists(schema_path):
        print(
            "No schema file found; "
            f"cannot create database: ({schema_path})"
        )
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read().strip()

    sql = text(schema_sql)
    db.session.execute(sql)
    db.session.commit()

    tables_in_db = tables()
    print(f"Created database from schema: {", ".join(tables_in_db)}")


def init_db():
    """Initialize the database with initial data."""
    tables_in_db = tables()
    if not tables_in_db:
        print("No tables found; cannot initialize database")
        return

    print("Initializing database")

    schema_path = os.path.join(os.path.dirname(
        __file__), "sql", "initial_data.sql")

    if not os.path.exists(schema_path):
        print(
            "No initial data file found; "
            f"skipping initialization: ({schema_path})"
        )
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        initial_data_sql = f.read().strip()

    sql = text(initial_data_sql)
    db.session.execute(sql)
    db.session.commit()

    print("Initialized database with initial data")


if __name__ == "__main__":  # pragma: no cover
    with app.app_context():
        setup_db()
        init_db()
