import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import repositories.citation_repository as repo
import repositories.citation_repository as citation_repository
from errors import CitationNotFoundError


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

        self.assertEqual(mock_db.session.execute.call_count, 5)

        args, kwargs = mock_db.session.execute.call_args_list[-1]
        sql = args[0]
        params = args[1]

        self.assertIn("DELETE FROM citations", str(sql))
        self.assertEqual(params["citation_id"], citation_id)
        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_delete_citation_early_returns_on_falsy_id(self, mock_db):
        repo.delete_citation(0)
        mock_db.session.execute.assert_not_called()
        mock_db.session.commit.assert_not_called()

    @patch("repositories.citation_repository.db")
    def test_delete_citation_removes_orphaned_links_and_entities(self, mock_db):
        citation_id = 42

        mock_select_cat = MagicMock()
        mock_select_cat.fetchall.return_value = [(1,), (2,)]

        mock_select_tag = MagicMock()
        mock_select_tag.fetchall.return_value = [(10,)]

        mock_del1 = MagicMock()
        mock_del2 = MagicMock()
        mock_del3 = MagicMock()
        mock_del4 = MagicMock()
        mock_del5 = MagicMock()
        mock_del6 = MagicMock()

        mock_db.session.execute.side_effect = [
            mock_select_cat,
            mock_select_tag,
            mock_del1,
            mock_del2,
            mock_del3,
            mock_del4,
            mock_del5,
            mock_del6,
        ]

        repo.delete_citation(citation_id)

        self.assertEqual(mock_db.session.execute.call_count, 8)

        args, kwargs = mock_db.session.execute.call_args_list[4]
        sql = args[0]
        params = args[1]
        self.assertIn("DELETE FROM citations", str(sql))
        self.assertEqual(params["citation_id"], citation_id)

        cat_delete_args, _ = mock_db.session.execute.call_args_list[5]
        self.assertIn("DELETE FROM categories", str(cat_delete_args[0]))
        self.assertIn("NOT EXISTS", str(cat_delete_args[0]))

        tag_delete_args, _ = mock_db.session.execute.call_args_list[7]
        self.assertIn("DELETE FROM tags", str(tag_delete_args[0]))
        self.assertIn("NOT EXISTS", str(tag_delete_args[0]))

        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_get_citation_returns_citation_object(self, mock_db):
        mock_row = SimpleNamespace(
            id=42, entry_type="book", citation_key="k42", fields={"title": "T42"})
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        citation = repo.get_citation_by_id(42)
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

    @patch("repositories.citation_repository.db")
    def test_get_citation_by_id_and_key_return_same_citation(self, mock_db):
        mock_row = SimpleNamespace(
            id=10,
            entry_type="book",
            citation_key="ck-10",
            fields={"title": "Some Title"},
        )

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        by_id = repo.get_citation_by_id(10)
        by_key = repo.get_citation_by_key("ck-10")

        self.assertEqual(mock_db.session.execute.call_count, 2)
        first_call_args, first_call_kwargs = mock_db.session.execute.call_args_list[0]
        second_call_args, second_call_kwargs = mock_db.session.execute.call_args_list[1]

        first_params = first_call_args[1] if len(
            first_call_args) > 1 else first_call_kwargs.get("params", {})
        second_params = second_call_args[1] if len(
            second_call_args) > 1 else second_call_kwargs.get("params", {})

        self.assertEqual(first_params.get("citation_id"), 10)
        self.assertNotIn("citation_key", first_params)

        self.assertEqual(second_params.get("citation_key"), "ck-10")
        self.assertNotIn("citation_id", second_params)

        self.assertIsNotNone(by_id)
        self.assertIsNotNone(by_key)

        # # UNNECESSARY. Here to satisfy type checker...
        if not by_id or not by_key:
            self.fail("Citations should not be None")

        self.assertEqual(by_id.id, by_key.id)
        self.assertEqual(by_id.entry_type, by_key.entry_type)
        self.assertEqual(by_id.citation_key, by_key.citation_key)
        self.assertEqual(by_id.fields, by_key.fields)

    @patch("repositories.citation_repository.db")
    def test_get_citation_by_key_returns_none_when_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        citation = repo.get_citation_by_key("nonexistent-key")
        self.assertIsNone(citation)

    @patch("repositories.citation_repository.db")
    def test_create_citation_returns_none_when_db_returns_none(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        out = repo.create_citation(1, "k-none", {"a": "b"})
        self.assertIsNone(out)

    @patch("repositories.citation_repository.create_citation")
    @patch("repositories.citation_repository.get_citation_by_key")
    def test_create_citation_with_metadata_raises_when_create_fails(self, mock_get_by_key, mock_create):
        mock_get_by_key.return_value = None
        mock_create.return_value = None
        entry_type = SimpleNamespace(id=2)

        with self.assertRaises(ValueError):
            repo.create_citation_with_metadata(entry_type, "kmeta", {})

    @patch("repositories.citation_repository.get_citation_by_key")
    def test_create_citation_with_metadata_raises_when_key_exists(self, mock_get_by_key):
        # simulate existing citation with same key -> should raise
        mock_get_by_key.return_value = SimpleNamespace(id=123)
        entry_type = SimpleNamespace(id=3)

        with self.assertRaises(ValueError):
            repo.create_citation_with_metadata(entry_type, "dup-key", {})

    @patch("repositories.citation_repository.get_citation_by_key")
    @patch("repositories.citation_repository.create_citation")
    @patch("repositories.citation_repository.assign_metadata_to_citation")
    def test_create_citation_with_metadata_success(self, mock_assign, mock_create, mock_get_by_key):
        mock_get_by_key.return_value = None
        created = SimpleNamespace(
            id=999, entry_type="book", citation_key="newkey", fields={})
        mock_create.return_value = created

        entry_type = SimpleNamespace(id=5)
        out = repo.create_citation_with_metadata(entry_type, "newkey", {}, categories=[
                                                 SimpleNamespace(id=1)], tags=[SimpleNamespace(id=2)])

        self.assertEqual(out.id, 999)
        mock_assign.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_validate_citation_raises_when_missing(self, mock_db):
        # get_citation_by_id will raise; ensure validate_citation propagates
        with patch("repositories.citation_repository.get_citation_by_id") as mock_get:
            mock_get.side_effect = repo.CitationNotFoundError if hasattr(
                repo, 'CitationNotFoundError') else Exception
            with self.assertRaises(Exception):
                repo.validate_citation(12345)

    @patch("repositories.citation_repository.db")
    def test_get_citations_by_ids_and_keys_empty_and_present(self, mock_db):
        # empty inputs should return []
        self.assertEqual(repo.get_citations_by_ids([]), [])
        self.assertEqual(repo.get_citations_by_keys([]), [])

        # now simulate db returning rows
        mock_row = SimpleNamespace(
            id=2, entry_type="book", citation_key="k2", fields={"t": "v"})
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.session.execute.return_value = mock_result

        out_ids = repo.get_citations_by_ids([2])
        out_keys = repo.get_citations_by_keys(["k2"])

        self.assertEqual(len(out_ids), 1)
        self.assertEqual(len(out_keys), 1)

    @patch("repositories.citation_repository.db")
    def test_get_citation_by_id_raises_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        with self.assertRaises(CitationNotFoundError):
            repo.get_citation_by_id(9999)

    @patch("repositories.citation_repository.db")
    def test_get_citations_by_ids_skips_falsey_rows(self, mock_db):
        # simulate a result list with one falsy row
        mock_row = SimpleNamespace(
            id=3, entry_type="book", citation_key="k3", fields={})
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [None, mock_row]
        mock_db.session.execute.return_value = mock_result

        out = repo.get_citations_by_ids([1, 3])
        self.assertEqual(len(out), 1)

    @patch("repositories.citation_repository.db")
    def test_update_citation_with_metadata_executes_deletes_and_assigns(self, mock_db):
        # ensure the deletion SQLs are executed and assign functions are called
        mock_db.session.execute.return_value = MagicMock()
        with patch("repositories.citation_repository.assign_categories_to_citation") as mock_assign_cats, \
                patch("repositories.citation_repository.assign_tags_to_citation") as mock_assign_tags:
            repo.update_citation_with_metadata(
                50, categories=[SimpleNamespace(id=1)], tags=[SimpleNamespace(id=2)])

        # expected two deletes (categories and tags) executed via db.session.execute
        self.assertTrue(mock_db.session.execute.called)
        mock_assign_cats.assert_called_once()
        mock_assign_tags.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_delete_citation_handles_empty_cat_tag_lists(self, mock_db):
        # simulate no cat/tag rows returned -> should still perform deletes and commit
        mock_select = MagicMock()
        mock_select.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_select

        repo.delete_citation(77)
        # multiple executes called for deletion SQLs and commit
        self.assertTrue(mock_db.session.execute.called)
        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_search_citations_filters_tags_and_categories(self, mock_db):
        mock_result = MagicMock()
        # return empty but ensure execute is called
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        queries = {"tags": ["A", "B"], "categories": ["X"],
                   "sort_by": "citation_key", "direction": "DESC"}
        out = repo.search_citations(queries)
        self.assertEqual(out, [])
        args, _ = mock_db.session.execute.call_args
        sql = str(args[0])
        self.assertIn("WHERE", sql)
        self.assertTrue(("t.name = ANY" in sql) or ("cat.name = ANY" in sql))

    @patch("repositories.citation_repository.db")
    def test_get_citations_normalizes_page_params(self, mock_db):
        # pass zero/negative page and per_page to trigger max(page,1) and max(per_page,1)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        out = repo.get_citations(page=0, per_page=-5)
        self.assertEqual(out, [])

        args, _ = mock_db.session.execute.call_args
        sql = args[0]
        params = args[1]
        # normalized per_page should be at least 1
        self.assertEqual(params.get("limit"), 1)
        self.assertEqual(params.get("offset"), 0)

    @patch("repositories.citation_repository.db")
    def test_get_citations_by_keys_skips_falsey_rows(self, mock_db):
        mock_row = SimpleNamespace(
            id=4, entry_type="book", citation_key="k4", fields={})
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [None, mock_row]
        mock_db.session.execute.return_value = mock_result

        out = repo.get_citations_by_keys(["x", "k4"])
        self.assertEqual(len(out), 1)

    @patch("repositories.citation_repository.db")
    def test_update_citation_with_metadata_only_categories_or_tags(self, mock_db):
        # ensure each branch (only categories / only tags) triggers the expected delete+assign
        mock_db.session.execute.return_value = MagicMock()
        with patch("repositories.citation_repository.assign_categories_to_citation") as mock_assign_cats:
            repo.update_citation_with_metadata(
                60, categories=[SimpleNamespace(id=7)])
        mock_assign_cats.assert_called_once()

        with patch("repositories.citation_repository.assign_tags_to_citation") as mock_assign_tags:
            repo.update_citation_with_metadata(
                61, tags=[SimpleNamespace(id=8)])
        mock_assign_tags.assert_called_once()

    @patch("repositories.citation_repository.db")
    def test_delete_citation_multiple_cat_and_tag_ids(self, mock_db):
        # simulate two category ids and two tag ids returned from initial selects
        mock_cat = MagicMock()
        mock_cat.fetchall.return_value = [(1,), (2,)]

        mock_tag = MagicMock()
        mock_tag.fetchall.return_value = [(10,), (11,)]

        # subsequent deletes return simple mocks
        mock_del = MagicMock()

        # side_effect sequence: cat_rows, tag_rows, delete ctc, delete ctt, delete citations, delete category 1, delete category 2, delete tag 10, delete tag 11
        mock_db.session.execute.side_effect = [
            mock_cat, mock_tag, mock_del, mock_del, mock_del, mock_del, mock_del, mock_del, mock_del]

        repo.delete_citation(123)

        # ensure execute called multiple times and commit invoked
        self.assertGreaterEqual(mock_db.session.execute.call_count, 9)
        mock_db.session.commit.assert_called_once()

    @patch("repositories.citation_repository.get_citation_by_id")
    def test_validate_citation_raises_when_get_returns_none(self, mock_get):
        # simulate get_citation_by_id returning None so validate_citation raises
        mock_get.return_value = None
        with self.assertRaises(CitationNotFoundError):
            repo.validate_citation(555)

    @patch("repositories.citation_repository.db")
    def test_get_citations_by_ids_returns_empty_when_db_returns_empty(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        out = repo.get_citations_by_ids([1, 2])
        self.assertEqual(out, [])

    @patch("repositories.citation_repository.db")
    def test_get_citations_by_keys_returns_empty_when_db_returns_empty(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        out = repo.get_citations_by_keys(["a", "b"])
        self.assertEqual(out, [])

    @patch("repositories.citation_repository.update_citation")
    def test_update_citation_with_metadata_passes_entry_type_id(self, mock_update):
        # ensure that providing an entry_type_id flows into update_citation
        repo.update_citation_with_metadata(88, entry_type_id=9)
        mock_update.assert_called_once()
        called_kwargs = mock_update.call_args[1]
        self.assertIn("entry_type_id", called_kwargs)
        self.assertEqual(called_kwargs["entry_type_id"], 9)

    @patch("repositories.citation_repository.get_citation_by_id")
    def test_validate_citation_no_raise_when_present(self, mock_get):
        # when get_citation_by_id returns a citation validate_citation should not raise
        mock_get.return_value = SimpleNamespace(id=1)
        # should not raise
        repo.validate_citation(1)


if __name__ == "__main__":
    unittest.main()
