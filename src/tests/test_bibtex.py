import unittest
from util import make_bibtex
from entities.book import Book

class TestMakeBibtex(unittest.TestCase):
    def test_make_bibtex_complete(self):
        book = Book(book_id=1, title="Sample Title", author="Sample Author",
                    year="2023", publisher="Sample Publisher", address="Sample Address")
        expected_bibtex = (
            "@book{1,\n"
            "  author = {Sample Author},\n"
            "  title = {Sample Title},\n"
            "  year = {2023},\n"
            "  publisher = {Sample Publisher},\n"
            "  address = {Sample Address},\n"
            "}"
        )
        self.assertEqual(make_bibtex(book), expected_bibtex)

    def test_make_bibtex_partial(self):
        book = Book(book_id=2, title="Another Title", author="Another Author",
                    year=None, publisher=None, address=None)
        expected_bibtex = (
            "@book{2,\n"
            "  author = {Another Author},\n"
            "  title = {Another Title},\n"
            "}"
        )
        self.assertEqual(make_bibtex(book), expected_bibtex)

    def test_make_bibtex_empty(self):
        book = Book(book_id=3, title=None, author=None,
                    year=None, publisher=None, address=None)
        expected_bibtex = (
            "@book{3,\n"
            "}"
        )
        self.assertEqual(make_bibtex(book), expected_bibtex)
