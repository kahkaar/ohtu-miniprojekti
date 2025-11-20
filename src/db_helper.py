import os

from sqlalchemy import text

from config import app, db


def reset_db():
    print("Clearing contents from all tables")
    table_list = tables()

    if not table_list:
        print("No tables found in database; creating database schema")
        setup_db()
        return

    for table in table_list:
        sql = text(f"DELETE FROM {table}")
        db.session.execute(sql)
    db.session.commit()


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
    tables_in_db = tables()
    if len(tables_in_db) > 0:
        print(f"Tables exist, dropping: {', '.join(tables_in_db)}")
        for table in tables_in_db:
            sql = text(f"DROP TABLE {table}")
            db.session.execute(sql)
        db.session.commit()

    print("Creating database")

    # Read schema from schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")
    with open(schema_path, 'r') as f:
        schema_sql = f.read().strip()

    sql = text(schema_sql)
    db.session.execute(sql)
    db.session.commit()

    tables_in_db = tables()
    print(f"Created database from schema: {', '.join(tables_in_db)}")


def init_db():
    """Initialize the database with initial data.
    """

    print("Initializing database")

    schema_path = os.path.join(os.path.dirname(
        __file__), "sql", "initial_data.sql")

    with open(schema_path, "r") as f:
        initial_data_sql = f.read().strip()

    sql = text(initial_data_sql)
    db.session.execute(sql)
    db.session.commit()

    print("Initialized database with initial data")


if __name__ == "__main__":
    with app.app_context():
        setup_db()
        init_db()
