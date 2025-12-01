import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import repositories.citation_repository as repo


class TestCitationRepository(unittest.TestCase):
    @patch("repositories.citation_repository.db")
    def test_get_citations_returns_citations_list(self, mock_db):
        rows = [
            SimpleNamespace(id=1, entry_type="book",
                            citation_key="k1", fields={"title": "T1"}),
            SimpleNamespace(id=2, entry_type="article",
                            citation_key="k2", fields={"title": "T2"}),
        ]

        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        citations = repo.get_citations()

        self.assertEqual(len(citations), 2)

        # # UNNECESSARY. Here to satisfy type checker...
        if not citations[0]:
            self.fail("Citations should not be None")

        self.assertEqual(citations[0].id, 1)
        self.assertEqual(citations[0].entry_type, "book")
        self.assertEqual(citations[0].citation_key, "k1")
        self.assertEqual(citations[0].fields, {"title": "T1"})

    @patch("repositories.citation_repository.db")
    def test_get_citations_returns_empty_list(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        citations = repo.get_citations()
        self.assertEqual(citations, [])

    @patch("repositories.citation_repository.db")
    def test_get_citations_with_paging(self, mock_db):
        rows = [
            SimpleNamespace(id=1, entry_type="book",
                            citation_key="k1", fields={"title": "T1"}),
            SimpleNamespace(id=2, entry_type="article",
                            citation_key="k2", fields={"title": "T2"}),
            SimpleNamespace(id=3, entry_type="misc",
                            citation_key="k3", fields={"title": "T3"}),
        ]

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [rows[1]]
        mock_db.session.execute.return_value = mock_result

        citations = repo.get_citations(page=2, per_page=1)
        self.assertEqual(len(citations), 1)

        # # UNNECESSARY. Here to satisfy type checker...
        if not citations[0]:
            self.fail("Citations should not be None")

        self.assertEqual(citations[0].id, 2)

    @patch("repositories.citation_repository.db")
    def test_get_citations_invalid_page_params(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        citations = repo.get_citations(page="x", per_page="y")
        self.assertEqual(citations, [])

    @patch("repositories.citation_repository.db")
    def test_get_citation_returns_none_when_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        citation = repo.get_citation(123)
        self.assertIsNone(citation)

    @patch("repositories.citation_repository.db")
    def test_create_citation_executes_insert(self, mock_db):
        entry_type_id = 1
        citation_key = "k3"
        fields = {"title": "T3"}

        repo.create_citation(entry_type_id, citation_key, fields)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertIn("INSERT INTO citations", str(sql))
        self.assertEqual(params["entry_type_id"], entry_type_id)
        self.assertEqual(params["citation_key"], citation_key)

        actual_fields = params["fields"]
        if isinstance(actual_fields, str):
            actual_fields = json.loads(actual_fields)
        self.assertEqual(actual_fields, fields)

    @patch("repositories.citation_repository.db")
    def test_create_citation_commits(self, mock_db):
        entry_type_id = 1
        citation_key = "k5"
        fields = {"title": "T5"}

        repo.create_citation(entry_type_id, citation_key, fields)

        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_update_citation_commits(self, mock_db):
        citation_id = 10
        entry_type_id = 2
        citation_key = "k10"
        fields = {"title": "Updated"}

        repo.update_citation(citation_id, entry_type_id, citation_key, fields)

        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_delete_citation_executes_and_commits(self, mock_db):
        citation_id = 7
        repo.delete_citation(citation_id)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertIn("DELETE FROM citations", str(sql))
        self.assertEqual(params["citation_id"], citation_id)
        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_get_citation_returns_citation_object(self, mock_db):
        mock_row = SimpleNamespace(
            id=42, entry_type="book", citation_key="k42", fields={"title": "T42"})
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        citation = repo.get_citation(42)
        self.assertIsNotNone(citation)

        # # UNNECESSARY. Here to satisfy type checker...
        if not citation:
            self.fail("Citation should not be None")

        self.assertEqual(citation.id, 42)
        self.assertEqual(citation.entry_type, "book")
        self.assertEqual(citation.citation_key, "k42")
        self.assertEqual(citation.fields, {"title": "T42"})

    @patch("repositories.citation_repository.db")
    def test_get_citations_single_param_no_paging(self, mock_db):
        rows = [SimpleNamespace(id=1, entry_type="book",
                                citation_key="k1", fields={"title": "T1"})]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        citations = repo.get_citations(page=2)
        self.assertEqual(len(citations), 1)

        citations = repo.get_citations(per_page=5)
        self.assertEqual(len(citations), 1)

    @patch("repositories.citation_repository.db")
    def test_update_citation_executes_update(self, mock_db):
        citation_id = 1
        entry_type_id = 2
        citation_key = "k4"
        fields = {"title": "Updated Title"}

        repo.update_citation(citation_id, entry_type_id, citation_key, fields)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertIn("UPDATE citations", str(sql))
        self.assertEqual(params["citation_id"], citation_id)
        self.assertEqual(params["entry_type_id"], entry_type_id)
        self.assertEqual(params["citation_key"], citation_key)

        actual_fields = params["fields"]
        if isinstance(actual_fields, str):
            actual_fields = json.loads(actual_fields)
        self.assertEqual(actual_fields, fields)

    @patch("repositories.citation_repository.db")
    def test_update_citation_noop_does_not_execute_or_commit(self, mock_db):
        repo.update_citation(99)
        mock_db.session.execute.assert_not_called()
        mock_db.session.commit.assert_not_called()

    @patch("repositories.citation_repository.db")
    def test_update_citation_partial_fields(self, mock_db):
        mock_result = MagicMock()
        mock_db.session.execute.return_value = mock_result

        repo.update_citation(5, citation_key="only-key")

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertIn("citation_key = :citation_key", str(sql))
        self.assertNotIn("entry_type_id", params)
        self.assertEqual(params["citation_key"], "only-key")
        self.assertEqual(params["citation_id"], 5)

    @patch("repositories.citation_repository.db")
    def test_get_citations_paging_params(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        repo.get_citations(page=3, per_page=5)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args

        params = args[1] if len(args) > 1 else kwargs.get("params", {})
        self.assertEqual(params.get("limit"), 5)
        self.assertEqual(params.get("offset"), 10)

    @patch("repositories.citation_repository.db")
    def test_update_citation_with_falsy_values_noops(self, mock_db):
        repo.update_citation(20, entry_type_id=0, citation_key="", fields={})
        mock_db.session.execute.assert_not_called()
        mock_db.session.commit.assert_not_called()

    def test_to_citation_object_handles_none(self):
        citation = repo._to_citation(None)
        self.assertIsNone(citation)

    def test_to_citation_object_handles_empty_fields(self):
        row = SimpleNamespace(
            id=3, entry_type="misc", citation_key="k3", fields=None)
        citation = repo._to_citation(row)
        self.assertIsNotNone(citation)

        # # UNNECESSARY. Here to satisfy type checker...
        if not citation:
            self.fail("Citation should not be None")

        self.assertEqual(citation.fields, {})

    @patch("repositories.citation_repository.db")
    def test_search_citations_returns_empty_when_no_queries(self, mock_db):
        result = repo.search_citations(None)
        self.assertEqual(result, [])

    @patch("repositories.citation_repository.db")
    def test_search_citations_builds_filters_and_params(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        queries = {
            "q": "alpha",
            "citation_key": "ck",
            "entry_type": "book",
            "author": "Bob",
            "year_from": "2000",
            "year_to": "2005",
            "sort_by": "year",
            "direction": "DESC",
        }

        out = repo.search_citations(queries)
        self.assertEqual(out, [])

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertEqual(params["q"], "%alpha%")
        self.assertEqual(params["citation_key"], "%ck%")
        self.assertEqual(params["entry_type"], "book")
        self.assertEqual(params["author"], "%Bob%")
        self.assertEqual(params["year_from"], 2000)
        self.assertEqual(params["year_to"], 2005)

        sql_str = str(sql)
        self.assertIn("WHERE", sql_str)
        self.assertIn("(c.fields->>'year')::int", sql_str)
        self.assertIn("ORDER BY (c.fields->>'year')::int DESC", sql_str)

    @patch("repositories.citation_repository.db")
    def test_search_citations_handles_nonint_years(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        queries = {"q": "x", "year_from": "notint",
                   "sort_by": "citation_key", "direction": "asc"}
        repo.search_citations(queries)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertNotIn("year_from", params)
        self.assertEqual(params.get("q"), "%x%")
        self.assertIn("ORDER BY c.citation_key ASC", str(sql))

    @patch("repositories.citation_repository.db")
    def test_search_citations_handles_missing_q_param(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        queries = {"year_from": "2001", "sort_by": "year", "direction": "desc"}
        repo.search_citations(queries)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertNotIn("q", params)
        self.assertEqual(params.get("year_from"), 2001)
        self.assertIn("ORDER BY (c.fields->>'year')::int DESC", str(sql))

    @patch("repositories.citation_repository.db")
    def test_search_sort_by_citation_key(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        queries = {"year_from": "2001",
                   "sort_by": "citation_key", "direction": "desc"}
        repo.search_citations(queries)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertNotIn("q", params)
        self.assertEqual(params.get("year_from"), 2001)
        self.assertIn("ORDER BY c.citation_key DESC", str(sql))

    @patch("repositories.citation_repository.db")
    def test_search_invalid_sort_by(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        queries = {"year_from": "2001",
                   "sort_by": "invalid_field", "direction": "desc"}
        repo.search_citations(queries)

        mock_db.session.execute.assert_called_once()
        args, kwargs = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]

        self.assertNotIn("q", params)
        self.assertEqual(params.get("year_from"), 2001)
        self.assertIn("ORDER BY c.id ASC", str(sql))


if __name__ == "__main__":
    unittest.main()
