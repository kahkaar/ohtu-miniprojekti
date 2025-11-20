import os
import unittest
from unittest.mock import MagicMock, patch

import db_helper


class TestDbHelper(unittest.TestCase):
    def setUp(self):
        # ensure TEST_ENV is set so app context related code paths are consistent
        os.environ.setdefault("TEST_ENV", "true")

    @patch("db_helper.db")
    def test_tables_returns_list(self, mock_db):
        # Arrange: mock execute to return rows with table names
        rows = [("books",), ("authors",)]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        # Act
        result = db_helper.tables()

        # Assert
        self.assertEqual(result, ["books", "authors"])

    @patch("db_helper.db")
    def test_tables_returns_empty_list(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        result = db_helper.tables()
        self.assertEqual(result, [])

    @patch("db_helper.open", create=True)
    @patch("db_helper.db")
    def test_setup_db_reads_schema_and_executes(self, mock_db, mock_open):
        # Arrange: no tables exist initially
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        # mock open to return a simple SQL
        mock_open.return_value.__enter__.return_value.read.return_value = "CREATE TABLE test(id INTEGER);"

        # Act
        db_helper.setup_db()

        # Assert that execute was called at least once with the schema
        self.assertTrue(mock_db.session.execute.called)
        # And commit was called
        mock_db.session.commit.assert_called()

    @patch("db_helper.open", create=True)
    @patch("db_helper.db")
    def test_setup_db_drops_existing_tables(self, mock_db, mock_open):
        # Arrange: simulate existing tables returned by tables()
        existing = ["books", "authors"]
        with patch.object(db_helper, 'tables', return_value=existing):
            # mock execute to accept DROP and CREATE statements
            mock_db.session.execute = MagicMock()
            mock_db.session.commit = MagicMock()

            # mock open to return a simple SQL
            mock_open.return_value.__enter__.return_value.read.return_value = "CREATE TABLE test(id INTEGER);"

            # Act
            db_helper.setup_db()

            # Assert: DROP executed once per existing table, and schema executed
            # So execute should be called at least len(existing) + 1 times
            self.assertGreaterEqual(
                mock_db.session.execute.call_count, len(existing) + 1)
            # commit should be called at least once (dropping and creating produce commits)
            self.assertGreaterEqual(mock_db.session.commit.call_count, 1)

    @patch("db_helper.db")
    def test_reset_db_deletes_tables_when_present(self, mock_db):
        # Arrange: tables returns a list
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("books",), ("authors",)]
        mock_db.session.execute.return_value = mock_result

        # Monkeypatch tables() to return two tables
        with patch.object(db_helper, 'tables', return_value=["books", "authors"]):
            db_helper.reset_db()

        # Expect DELETE executed for each table and commit called
        # We can't assert exact SQL object, but ensure execute called twice
        self.assertGreaterEqual(mock_db.session.execute.call_count, 2)
        mock_db.session.commit.assert_called()

    @patch("db_helper.db")
    def test_reset_db_calls_setup_when_no_tables(self, mock_db):
        # Arrange: make tables() return empty
        with patch.object(db_helper, 'tables', return_value=[]):
            with patch.object(db_helper, 'setup_db') as mock_setup:
                db_helper.reset_db()
                mock_setup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
