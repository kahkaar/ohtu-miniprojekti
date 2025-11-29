
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

        posted = util.get_posted_fields(form)

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


if __name__ == "__main__":
    unittest.main()
