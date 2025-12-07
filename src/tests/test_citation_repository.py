import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import repositories.citation_repository as repo
import repositories.citation_repository as citation_repository


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

        citation = repo.get_citation_by_id(123)
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
    @patch("repositories.citation_repository.assign_tags_to_citation")
    @patch("repositories.citation_repository.assign_category_to_citation")
    @patch("repositories.citation_repository.get_citation_by_key")
    def test_create_citation_with_metadata_assigns_category_and_tags(self, mock_get_by_key, mock_assign_category, mock_assign_tags, mock_create):
        mock_get_by_key.return_value = None
        mock_create.return_value = SimpleNamespace(id=99)

        entry_type = SimpleNamespace(id=2)
        category = SimpleNamespace(id=5)
        tags = ["t1", "t2"]

        out = repo.create_citation_with_metadata(
            entry_type, "kmeta", {"x": 1}, category=category, tags=tags)

        mock_create.assert_called_once()
        mock_assign_category.assert_called_once_with(99, 5)
        mock_assign_tags.assert_called_once_with(99, tags)
        self.assertIsNotNone(out)

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

    @patch("repositories.citation_repository.create_citation")
    @patch("repositories.citation_repository.assign_tags_to_citation")
    @patch("repositories.citation_repository.assign_category_to_citation")
    @patch("repositories.citation_repository.get_citation_by_key")
    def test_create_citation_with_metadata_ignores_tags_when_not_list(self, mock_get_by_key, mock_assign_category, mock_assign_tags, mock_create):
        # get_citation_by_key returns None, create_citation returns an object
        mock_get_by_key.return_value = None
        mock_create.return_value = SimpleNamespace(id=9)

        # call with tags that are not a list and no category -> neither assign fn should be called
        out = repo.create_citation_with_metadata(SimpleNamespace(
            id=4), "ck2", {"b": 2}, category=None, tags='not-a-list')

        mock_create.assert_called_once()
        mock_assign_category.assert_not_called()
        mock_assign_tags.assert_not_called()
        self.assertIsNotNone(out)

    @patch("repositories.citation_repository.db")
    @patch("repositories.citation_repository.update_citation")
    @patch("repositories.citation_repository.assign_tags_to_citation")
    @patch("repositories.citation_repository.assign_category_to_citation")
    def test_update_citation_with_metadata_assigns_category_and_tags(self, mock_assign_category, mock_assign_tags, mock_update, mock_db):
        citation_id = 77

        category = SimpleNamespace(id=5)
        tags = ["tag1", "tag2"]

        repo.update_citation_with_metadata(
            citation_id,
            citation_key="k-upd",
            fields={"title": "X"},
            category=category,
            tags=tags,
        )

        mock_update.assert_called_once_with(
            citation_id=citation_id, citation_key="k-upd", fields={"title": "X"})
        mock_assign_category.assert_called_once_with(citation_id, 5)
        mock_assign_tags.assert_called_once_with(citation_id, tags)

    @patch("repositories.citation_repository.db")
    @patch("repositories.citation_repository.update_citation")
    @patch("repositories.citation_repository.assign_tags_to_citation")
    @patch("repositories.citation_repository.assign_category_to_citation")
    def test_update_citation_with_metadata_assigns_category_only_when_tags_not_list(self, mock_assign_category, mock_assign_tags, mock_update, mock_db):
        citation_id = 88

        category = SimpleNamespace(id=6)
        tags = "not-a-list"

        repo.update_citation_with_metadata(
            citation_id,
            citation_key="k-upd2",
            fields={"title": "Y"},
            category=category,
            tags=tags,
        )

        mock_update.assert_called_once_with(
            citation_id=citation_id, citation_key="k-upd2", fields={"title": "Y"})
        mock_assign_category.assert_called_once_with(citation_id, 6)
        mock_assign_tags.assert_not_called()

    @patch("repositories.citation_repository.update_citation")
    @patch("repositories.citation_repository.assign_tags_to_citation")
    @patch("repositories.citation_repository.assign_category_to_citation")
    def test_update_citation_with_metadata_calls_update_only_when_no_category_or_tags(self, mock_assign_category, mock_assign_tags, mock_update):
        citation_id = 99

        repo.update_citation_with_metadata(
            citation_id,
            citation_key="k-none",
            fields={"title": "Z"},
            category=None,
            tags=None,
        )

        mock_update.assert_called_once_with(
            citation_id=citation_id, citation_key="k-none", fields={"title": "Z"})
        mock_assign_category.assert_not_called()
        mock_assign_tags.assert_not_called()


if __name__ == "__main__":
    unittest.main()
