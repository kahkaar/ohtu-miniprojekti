import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import db_helper
from app import app

os.environ.setdefault("TEST_ENV", "true")


class TestBook(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        # ensure reset_db runs inside the Flask application context
        self.app = app
        with self.app.app_context():
            db_helper.reset_db()

        self.client = self.app.test_client()

    @patch("app.get_books")
    def test_citations_page_shows_books(self, mock_get_books):
        # Arrange: stub get_books to return a single book-like object
        book = SimpleNamespace(
            author="Jane Doe",
            year=2020,
            title="Example Book",
            publisher="Fiction House",
            address="New York",
        )
        mock_get_books.return_value = [book]

        # Act
        resp = self.client.get("/citations")
        body = resp.get_data(as_text=True)

        # Assert
        self.assertIn("Jane Doe (2020)", body)
        self.assertIn("Example Book", body)
        self.assertIn("Fiction House", body)
        self.assertIn("New York", body)

    @patch("app.create_book")
    def test_post_creates_book_and_redirects(self, mock_create_book):
        # Act: post data to create a book
        response = self.client.post(
            "/",
            data={
                "title": "New Title",
                "author": "Author X",
                "year": "1999",
                "publisher": "Pub",
                "address": "City",
            },
            follow_redirects=False,
        )

        # Assert create_book was called with the provided values
        mock_create_book.assert_called_once_with(
            "New Title", "Author X", "1999", "Pub", "City"
        )

        # POST should redirect to index on success
        self.assertEqual(response.status_code, 302)

    @patch("app.create_book")
    def test_post_shows_flash_on_success(self, mock_create_book):
        # follow redirects to capture flashed message rendered in layout
        response = self.client.post(
            "/",
            data={
                "title": "New Title",
                "author": "Author X",
                "year": "1999",
                "publisher": "Pub",
                "address": "City",
            },
            follow_redirects=True,
        )

        body = response.get_data(as_text=True)
        # layout includes flashes; the app flashes "Book added successfully!"
        self.assertIn("Book added successfully!", body)

    @patch("app.create_book")
    def test_post_missing_fields_does_not_call_create(self, mock_create_book):
        # missing title should not call create_book and should redirect back
        response = self.client.post(
            "/",
            data={
                "title": "",
                "author": "",
            },
            follow_redirects=False,
        )

        mock_create_book.assert_not_called()
        self.assertEqual(response.status_code, 302)

    @patch("app.get_books")
    def test_citations_shows_empty_message(self, mock_get_books):
        mock_get_books.return_value = []
        resp = self.client.get("/citations")
        body = resp.get_data(as_text=True)
        self.assertIn("No saved citations yet.", body)

    def test_book_str_method(self):
        from entities.book import Book

        book = Book(
            id=1,
            title="Sample Title",
            author="Sample Author",
            year=2021,
            publisher="Sample Publisher",
            address="Sample Address",
        )
        expected_str = "Sample Title by Sample Author, 2021, Sample Publisher, Sample Address"
        self.assertEqual(str(book), expected_str)

    @patch("app.delete_book")
    def test_delete_citation_calls_delete_and_redirects(self, mock_delete_book):
        response = self.client.get("/citations/delete/1", follow_redirects=False)

        mock_delete_book.assert_called_once_with(1)

        self.assertEqual(response.status_code, 302)
        
