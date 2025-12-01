import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import repositories.entry_type_repository as repo


class TestEntryTypeRepository(unittest.TestCase):
    @patch("repositories.entry_type_repository.db")
    def test_get_entry_types_returns_list(self, mock_db):
        rows = [
            SimpleNamespace(id=1, name="article"),
            SimpleNamespace(id=2, name="book"),
        ]

        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        types = repo.get_entry_types()
        self.assertEqual(len(types), 2)
        self.assertEqual(types[0].id, 1)
        self.assertEqual(types[0].name, "article")

        # ensure the SQL contains the table name
        mock_db.session.execute.assert_called_once()
        sql = mock_db.session.execute.call_args[0][0]
        self.assertIn("FROM entry_types", str(sql))

    @patch("repositories.entry_type_repository.db")
    def test_get_entry_types_empty(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        types = repo.get_entry_types()
        self.assertEqual(types, [])

    @patch("repositories.entry_type_repository.db")
    def test_get_entry_type_by_id_found(self, mock_db):
        mock_row = SimpleNamespace(id=42, name="custom")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        et = repo.get_entry_type(42)
        self.assertIsNotNone(et)
        # # UNNECESSARY. Here to satisfy type checker...
        if not et:
            self.fail("Entry Type should not be None")

        self.assertEqual(et.id, 42)
        self.assertEqual(et.name, "custom")

        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertIn("WHERE id = :entry_type_id", str(sql))
        self.assertEqual(params["entry_type_id"], 42)

    @patch("repositories.entry_type_repository.db")
    def test_get_entry_type_by_id_none(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        et = repo.get_entry_type(999)
        self.assertIsNone(et)

    @patch("repositories.entry_type_repository.db")
    def test_get_entry_type_by_name_found(self, mock_db):
        mock_row = SimpleNamespace(id=7, name="misc")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        et = repo.get_entry_type_by_name("misc")
        self.assertIsNotNone(et)
        # # UNNECESSARY. Here to satisfy type checker...
        if not et:
            self.fail("Entry Type should not be None")

        self.assertEqual(et.id, 7)
        self.assertEqual(et.name, "misc")

        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertIn("WHERE name = :entry_type", str(sql))
        self.assertEqual(params["entry_type"], "misc")

    @patch("repositories.entry_type_repository.db")
    def test_get_entry_type_by_name_none(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        et = repo.get_entry_type_by_name("nope")
        self.assertIsNone(et)


if __name__ == "__main__":
    unittest.main()
