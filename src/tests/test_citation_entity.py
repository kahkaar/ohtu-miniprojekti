import unittest

from entities.citation import Citation


class TestCitationEntity(unittest.TestCase):
    def test_to_human_readable_article(self):
        fields = {
            "author": "Doe, J.",
            "year": "2020",
            "title": "On Testing",
            "journaltitle": "Journal of Tests",
            "volume": "12",
            "number": "3",
            "pages": "10-20",
        }

        c = Citation(1, "article", "doe2020", fields)

        expected = "Doe, J. (2020). On Testing. Journal of Tests, 12(3), pp. 10-20."
        self.assertEqual(c.to_human_readable(), expected)

    def test_to_human_readable_book_prefers_booktitle(self):
        fields = {
            "author": "Smith, A.",
            "year": "1999",
            "title": "Collected Works",
            "booktitle": "Collected Works Vol. 1",
            "publisher": "Acme",
        }

        c = Citation(2, "book", "smith1999", fields)
        expected = "Smith, A. (1999). Collected Works. Collected Works Vol. 1."
        self.assertEqual(c.to_human_readable(), expected)

    def test_to_human_readable_fallback_on_empty(self):
        c = Citation(3, "misc", "k-empty", {})
        self.assertEqual(c.to_human_readable(), "k-empty (misc)")

    def test_to_compact_short_and_truncated(self):
        fields_short = {"title": "T1", "author": "A1"}
        c_short = Citation(4, "book", "k-short", fields_short)
        self.assertEqual(c_short.to_compact(), "book — k-short — A1, T1")

        fields_many = {"a": "1", "b": "2", "c": "3", "d": "4"}
        c_many = Citation(5, "article", "k-many", fields_many)
        self.assertEqual(c_many.to_compact(),
                         "article — k-many — 1, 2, 3, ...")

    def test_to_bibtex_contains_fields_and_structure(self):
        fields = {"title": "T1", "author": "A1"}
        c = Citation(6, "book", "k-bib", fields)
        out = c.to_bibtex()
        self.assertTrue(out.startswith("@book{k-bib,"))
        self.assertIn("title = {T1}", out)
        self.assertIn("author = {A1}", out)

    def test_to_dict_and_str_and_repr(self):
        fields = {"title": "T2"}
        c = Citation(7, "misc", "k7", fields)

        d = c.to_dict()
        self.assertEqual(d["id"], 7)
        self.assertEqual(d["entry_type"], "misc")
        self.assertEqual(d["citation_key"], "k7")
        self.assertEqual(d["fields"], fields)

        s = str(c)
        self.assertTrue(s.startswith("@misc{k7,"))

        r = repr(c)
        self.assertIn("citation_key", r)
        self.assertIn("k7", r)


if __name__ == "__main__":
    unittest.main()
