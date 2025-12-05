
import unittest

from flask import Flask

import util


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = "test-secret"

    def test_sanitize_str_and_non_str(self):
        self.assertEqual(util.sanitize("  hello   world \n"), "hello world")
        self.assertEqual(util.sanitize(123), 123)

    def test_validate(self):
        self.assertEqual(util.validate("ok"), "ok")
        self.assertIsNone(util.validate(""))
        self.assertIsNone(util.validate("   "))
        self.assertIsNone(util.validate(None))

    def test_collapse_whitespace(self):
        self.assertEqual(util.collapse_whitespace(" a b \n c "), "abc")
        self.assertEqual(util.collapse_whitespace(5), 5)

    def test_get_posted_fields_filters_and_sanitizes(self):
        form = {
            "title": "  A  title ",
            "citation_key": " should-be-ignored",
            "entry_type": "book",
            "author": " John   Doe ",
            "empty": "   ",
        }

        posted = util.extract_fields(form)

        self.assertNotIn("citation_key", posted)
        self.assertNotIn("entry_type", posted)
        self.assertEqual(posted.get("title"), "A title")
        self.assertEqual(posted.get("author"), "John Doe")
        self.assertNotIn("empty", posted)

    def test_session_helpers(self):
        with self.app.test_request_context():
            util.set_session("foo", "bar")
            self.assertEqual(util.get_session("foo"), "bar")
            self.assertEqual(util.get_session("nope", "default"), "default")

            util.set_session("to_clear", "x")
            util.clear_session("to_clear")
            self.assertIsNone(util.get_session("to_clear"))

            util.set_session("a", 1)
            util.set_session("b", 2)
            util.clear_session()
            self.assertIsNone(util.get_session("a"))
            self.assertIsNone(util.get_session("b"))

    def test_parse_search_queries_from_util(self):
        args = {
            "q": "  spaced out  ",
            "citation_key": " AbC123 ",
            "author": " John Doe ",
            "year_from": "1990",
            "year_to": "1999",
            "sort_by": "citation_key",
            "direction": "Down",
        }

        parsed = util.parse_search_queries(args)

        self.assertEqual(parsed["q"], "spaced out")
        self.assertEqual(parsed["citation_key"], "abc123")
        self.assertEqual(parsed["author"], "john doe")
        self.assertEqual(parsed["year_from"], 1990)
        self.assertEqual(parsed["year_to"], 1999)
        self.assertEqual(parsed["sort_by"], "citation_key")

        self.assertIn(parsed["direction"], ("ASC", "DESC"))

    def test_parse_search_queries_edge_cases(self):
        parsed = util.parse_search_queries({})
        self.assertIsNone(parsed["sort_by"])
        self.assertEqual(parsed["direction"], "ASC")

        parsed = util.parse_search_queries({"year_from": "abc", "year_to": ""})
        self.assertIsNone(parsed["year_from"])
        self.assertIsNone(parsed["year_to"])

    def test_parse_search_queries_int_years_and_variants(self):
        args = {"year_from": 2015, "year_to": 2020,
                "sort_by": "Year", "direction": "desc"}
        parsed = util.parse_search_queries(args)
        self.assertEqual(parsed["year_from"], 2015)
        self.assertEqual(parsed["year_to"], 2020)
        self.assertEqual(parsed["sort_by"], "year")
        self.assertEqual(parsed["direction"], "DESC")

    def test_parse_search_queries_invalid_direction_and_blank_fields(self):
        args = {"direction": "down", "citation_key": "   ",
                "author": None, "q": "\n  "}
        parsed = util.parse_search_queries(args)
        self.assertEqual(parsed["direction"], "ASC")
        self.assertEqual(parsed["citation_key"], "")
        self.assertEqual(parsed["author"], "")
        self.assertEqual(parsed["q"], "")

    def test_parse_search_queries_handles_str_exception_in_year(self):
        class BadStr:
            def __str__(self):
                raise TypeError("bad to-string")

        parsed = util.parse_search_queries(
            {"year_from": BadStr(), "year_to": BadStr()})
        self.assertIsNone(parsed["year_from"])
        self.assertIsNone(parsed["year_to"])


if __name__ == "__main__":
    unittest.main()


class TestUtilExtensions(unittest.TestCase):
    def test_parse_entry_type_and_conversions(self):
        self.assertIsNone(util.parse_entry_type(None))

        parsed = util.parse_entry_type({"id": 7, "name": "misc"})
        self.assertIsNotNone(parsed)

        # # UNNECESSARY. Here to satisfy type checker...
        if not parsed:
            self.fail("Parsed EntryType should not be None")

        self.assertEqual(parsed.id, 7)
        self.assertEqual(parsed.name, "misc")

    def test_extract_category_and_tags_and_key_variants(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        f = DummyForm({"category": "  Cat XX  ", "tags": [" One ", "", "Two"]})
        self.assertEqual(util.extract_category(f), "Cat XX")
        self.assertEqual(util.extract_tags(f), ["One", "Two"])

        fk = DummyForm({"citation_key": " My Key  "})
        self.assertEqual(util.extract_citation_key(fk), "My-Key")

        fk2 = DummyForm({"citation_key": "   "})
        self.assertIsNone(util.extract_citation_key(fk2))

    def test_to_category_and_to_tag_and_to_citation_json_variants(self):
        row_cat = type("R", (), {"id": 1, "name": "C1"})
        cat = util.to_category(row_cat)
        self.assertEqual(cat.id, 1)
        self.assertEqual(cat.name, "C1")

        row_tag = type("R", (), {"id": 2, "name": "T1"})
        tag = util.to_tag(row_tag)
        self.assertEqual(tag.id, 2)
        self.assertEqual(tag.name, "T1")

        row = type("R", (), {"id": 3, "entry_type": "book",
                   "citation_key": "k3", "fields": {"a": 1}})
        c = util.to_citation(row)

        if not c:
            self.fail("Citation should not be None")
        self.assertEqual(c.fields, {"a": 1})

        row2 = type("R", (), {"id": 4, "entry_type": "book",
                    "citation_key": "k4", "fields": '{"a":2}'})
        c2 = util.to_citation(row2)

        if not c2:
            self.fail("Citation should not be None")
        self.assertEqual(c2.fields, {"a": 2})

        row3 = type("R", (), {"id": 5, "entry_type": "book",
                    "citation_key": "k5", "fields": 'not json'})
        c3 = util.to_citation(row3)

        # # UNNECESSARY. Here to satisfy type checker...
        if not c3:
            self.fail("Citation should not be None")
        self.assertEqual(c3.fields, {})

    def test_extract_category_edgecases(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

        self.assertIsNone(util.extract_category(DummyForm({})))

        self.assertIsNone(util.extract_category(DummyForm({"category": ""})))
        self.assertIsNone(util.extract_category(
            DummyForm({"category": "   "})))

        self.assertIsNone(util.extract_category(DummyForm({"category": 0})))

        self.assertEqual(util.extract_category(
            DummyForm({"category": "0"})), "0")

    def test_extract_category_new_precedence_and_empty_new(self):
        class DummyFormBoth:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

        # new category provided should take precedence and be sanitized
        f_new = DummyFormBoth(
            {"category_new": "  New Cat ", "category": "Old"})
        self.assertEqual(util.extract_category(f_new), "New Cat")

        # new category provided but empty -> fallback to category
        f_new_empty = DummyFormBoth(
            {"category_new": "   ", "category": "  Fallback "})
        self.assertEqual(util.extract_category(f_new_empty), "Fallback")

    def test_collapse_and_hyphens_and_none_citation(self):
        self.assertEqual(util.collapse_to_hyphens(" A B C "), "A-B-C")

        self.assertEqual(util.collapse_to_hyphens(123), 123)

    def test_to_citation_none(self):
        self.assertIsNone(util.to_citation(None))

    def test_to_entry_type_none_handling(self):
        row = type("R", (), {"id": 9, "name": "custom"})
        et = util.to_entry_type(row)
        self.assertEqual(et.id, 9)
        self.assertEqual(et.name, "custom")


class TestUtilTagsExtra(unittest.TestCase):
    def test_extract_tags_with_tags_new_and_dedup(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        # existing tags a,b and new tags 'b, c, , a' should produce ['a','b','c']
        f = DummyForm({"tags": ["a", "b"], "tags_new": "b, c, , a "})
        out = util.extract_tags(f)
        self.assertEqual(out, ["a", "b", "c"])

    def test_extract_tags_blank_and_missing(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        # no tags present
        f_empty = DummyForm({})
        self.assertEqual(util.extract_tags(f_empty), [])

        # tags_new provided but only whitespace -> should be ignored
        f_blank_new = DummyForm({"tags_new": "   ,  ,\t"})
        self.assertEqual(util.extract_tags(f_blank_new), [])


class TestToCitationVariants(unittest.TestCase):
    def test_to_citation_with_dict_fields_and_list_tags(self):
        row = type("R", (), {
            "id": 10,
            "entry_type": "article",
            "citation_key": "k10",
            "fields": {"a": 1},
            "tags": ["t1", "t2"],
            "categories": ["c1"],
        })
        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.fields, {"a": 1})
        self.assertEqual(c.tags, ["t1", "t2"])
        self.assertEqual(c.categories, ["c1"])

    def test_to_citation_with_json_string_fields_and_json_tags(self):
        row = type("R", (), {
            "id": 11,
            "entry_type": "book",
            "citation_key": "k11",
            "fields": '{"b":2}',
            "tags": '["x","y"]',
            "categories": '["catA"]',
        })
        c = util.to_citation(row)
        self.assertEqual(c.fields, {"b": 2})
        self.assertEqual(c.tags, ["x", "y"])
        self.assertEqual(c.categories, ["catA"])

    def test_to_citation_with_comma_separated_tags_and_categories(self):
        row = type("R", (), {
            "id": 12,
            "entry_type": "misc",
            "citation_key": "k12",
            "fields": '{}',
            "tags": 'a, b, , c',
            "categories": ' c1, c2 ',
        })
        c = util.to_citation(row)
        self.assertEqual(c.tags, ["a", "b", "c"])
        self.assertEqual(c.categories, ["c1", "c2"])

    def test_to_citation_with_none_tags_and_categories(self):
        row = type("R", (), {
            "id": 13,
            "entry_type": "misc",
            "citation_key": "k13",
            "fields": None,
            "tags": None,
            "categories": None,
        })
        c = util.to_citation(row)
        self.assertEqual(c.fields, {})
        self.assertEqual(c.tags, [])
        self.assertEqual(c.categories, [])

    def test_to_citation_with_unexpected_iterable(self):
        class IterableLike:
            def __iter__(self):
                yield 'i1'
                yield 'i2'

        row = type("R", (), {
            "id": 14,
            "entry_type": "misc",
            "citation_key": "k14",
            "fields": {},
            "tags": IterableLike(),
            "categories": IterableLike(),
        })
        c = util.to_citation(row)

        if not c:
            self.fail("to_citation returned None unexpectedly.")

        self.assertEqual(c.tags, ['i1', 'i2'])
        self.assertEqual(c.categories, ['i1', 'i2'])

    def test_to_citation_with_non_iterable_truthy_triggers_typeerror(self):
        # An object that is truthy but not iterable should cause list(obj)
        # to raise TypeError and _to_list should return an empty list.
        class NotIterable:
            pass

        row = type("R", (), {
            "id": 15,
            "entry_type": "misc",
            "citation_key": "k15",
            "fields": {},
            "tags": NotIterable(),
            "categories": NotIterable(),
        })

        c = util.to_citation(row)

        if not c:
            self.fail("to_citation returned None unexpectedly.")

        self.assertEqual(c.tags, [])
        self.assertEqual(c.categories, [])
