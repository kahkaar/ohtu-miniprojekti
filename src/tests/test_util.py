
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
