import os
import unittest
from unittest.mock import MagicMock, patch

import db_helper


class TestDbHelper(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault("TEST_ENV", "true")

    @patch("db_helper.db")
    def test_tables_returns_list(self, mock_db):
        rows = [("books",), ("authors",)]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        result = db_helper.tables()

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
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        mock_open.return_value.__enter__.return_value.read.return_value = "CREATE TABLE test(id INTEGER);"

        # Act
        db_helper.setup_db()

        self.assertTrue(mock_db.session.execute.called)
        mock_db.session.commit.assert_called()

    @patch("db_helper.open", create=True)
    @patch("db_helper.db")
    def test_setup_db_drops_existing_tables(self, mock_db, mock_open):
        existing = ["books", "authors"]
        with patch.object(db_helper, 'tables', return_value=existing):
            mock_db.session.execute = MagicMock()
            mock_db.session.commit = MagicMock()

            mock_open.return_value.__enter__.return_value.read.return_value = "CREATE TABLE test(id INTEGER);"

            db_helper.setup_db()

            self.assertGreaterEqual(
                mock_db.session.execute.call_count, len(existing) + 1)
            self.assertGreaterEqual(mock_db.session.commit.call_count, 1)

    @patch("db_helper.db")
    def test_reset_db_deletes_tables_when_present(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("books",), ("authors",)]
        mock_db.session.execute.return_value = mock_result

        with patch.object(db_helper, 'tables', return_value=["books", "authors"]):
            db_helper.reset_db()

        self.assertGreaterEqual(mock_db.session.execute.call_count, 2)
        mock_db.session.commit.assert_called()

    @patch("db_helper.db")
    def test_reset_db_calls_setup_when_no_tables(self, mock_db):
        with patch.object(db_helper, 'tables', return_value=[]):
            with patch.object(db_helper, 'setup_db') as mock_setup:
                db_helper.reset_db()
                mock_setup.assert_called_once()

    def test_validate_identifier_accepts_good(self):
        self.assertEqual(db_helper._validate_identifier("books"), "books")

    def test_validate_identifier_rejects_non_string(self):
        with self.assertRaises(ValueError):
            db_helper._validate_identifier(None)

    def test_validate_identifier_rejects_bad_chars(self):
        with self.assertRaises(ValueError):
            db_helper._validate_identifier("bad-name")

    @patch("db_helper.db")
    def test_setup_db_no_schema_file(self, mock_db):
        with patch.object(db_helper, 'tables', return_value=[]):
            with patch.object(db_helper.os.path, 'exists', return_value=False):
                db_helper.setup_db()

        self.assertFalse(mock_db.session.execute.called)

    @patch("db_helper.db")
    def test_init_db_no_tables_returns(self, mock_db):
        with patch.object(db_helper, 'tables', return_value=[]):
            db_helper.init_db()

        self.assertFalse(mock_db.session.execute.called)

    @patch("db_helper.db")
    def test_init_db_missing_initial_data(self, mock_db):
        with patch.object(db_helper, 'tables', return_value=['books']):
            with patch.object(db_helper.os.path, 'exists', return_value=False):
                db_helper.init_db()

        self.assertFalse(mock_db.session.execute.called)

    def test_reset_db_raises_on_invalid_identifier(self):
        with patch.object(db_helper, 'tables', return_value=["bad-name"]):
            with patch("db_helper.db"):
                with self.assertRaises(ValueError):
                    db_helper.reset_db()


if __name__ == "__main__":
    unittest.main()
