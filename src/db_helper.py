import os

from sqlalchemy import text

from config import app, db


def reset_db():
    """Clears all contents from all tables in the database.
    Used mainly for unit tests.
    """
    print("Clearing contents from all tables")

    tables_in_db = tables()
    if not tables_in_db:
        print("No tables found; creating schema and initializing data")
        setup_db()
        init_db()
        return

    for table in tables_in_db:
        sql = text(f"DELETE FROM {table}")
        db.session.execute(sql)
    db.session.commit()

    print("Cleared database contents. Tables: " + ", ".join(tables_in_db))


def tables():
    """Returns all table names from the database except those ending with _id_seq"""
    sql = text(
        "SELECT table_name "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public' "
        "AND table_name NOT LIKE '%_id_seq'"
    )

    result = db.session.execute(sql)
    return [row[0] for row in result.fetchall()]


def setup_db():
    """
      Creating the database
      If database tables already exist, those are dropped before the creation
    """
    print("Creating database")

    # Drop existing tables. schema.sql should have drop table if exists aswell.
    tables_in_db = tables()
    if tables_in_db:
        print(f"Tables exist, dropping: {", ".join(tables_in_db)}")
        for table in tables_in_db:
            sql = text(f"DROP TABLE IF EXISTS {table} CASCADE")
            db.session.execute(sql)
        db.session.commit()

    # Read schema from schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    if not os.path.exists(schema_path):
        print(f"No schema file found, cannot create database: {schema_path}")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read().strip()

    sql = text(schema_sql)
    db.session.execute(sql)
    db.session.commit()

    tables_in_db = tables()
    print("Created database from schema: " + ", ".join(tables_in_db))


def init_db():
    """Initialize the database with initial data.
    """
    print("Initializing database")

    schema_path = os.path.join(os.path.dirname(
        __file__), "sql", "initial_data.sql")

    if not os.path.exists(schema_path):
        print("No initial data file found, skipping initialization")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        initial_data_sql = f.read().strip()

    sql = text(initial_data_sql)
    db.session.execute(sql)
    db.session.commit()

    print("Initialized database with initial data")


if __name__ == "__main__":
    with app.app_context():
        setup_db()
        init_db()
