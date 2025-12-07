import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import repositories.entry_fields_repository as repo


class TestEntryFieldsRepository(unittest.TestCase):
    @patch("repositories.entry_fields_repository.db")
    def test_get_entry_fields_returns_list(self, mock_db):
        rows = [SimpleNamespace(name="author"), SimpleNamespace(name="title")]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        fields = repo.get_entry_fields(1)
        self.assertEqual(fields, ["author", "title"])

        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertIn("default_entry_fields", str(sql))
        self.assertEqual(params["entry_type_id"], 1)

    @patch("repositories.entry_fields_repository.db")
    def test_get_entry_fields_empty(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        fields = repo.get_entry_fields(999)
        self.assertEqual(fields, [])

    @patch("repositories.entry_fields_repository.db")
    def test_get_default_fields_returns_list(self, mock_db):
        rows = [MagicMock(name='abstract'), MagicMock(name='title')]
        rows = [type('R', (), {'name': 'abstract'})(),
                type('R', (), {'name': 'title'})()]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        fields = repo.get_default_fields()
        self.assertEqual(fields, ['abstract', 'title'])


if __name__ == "__main__":
    unittest.main()
