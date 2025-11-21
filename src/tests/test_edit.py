import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import db_helper
from app import app

os.environ.setdefault("TEST_ENV", "true")


class TestEdit(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app

        # Ensure DB is reset inside Flask app context
        with self.app.app_context():
            db_helper.reset_db()

        self.client = self.app.test_client()

    @patch("app.get_book")
    def test_edit_page_prefills_form(self, mock_get_book):
        """GET /edit/<id> shows form with current book details filled in."""
        book = SimpleNamespace(
            id=1,
            title="Old Title",
            author="Old Author",
            year="2000",
            publisher="Old Publisher",
            address="Old Address",)
        mock_get_book.return_value = book

        resp = self.client.get("/edit/1")
        body = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('value="Old Title"', body)
        self.assertIn('value="Old Author"', body)
        self.assertIn('value="2000"', body)
        self.assertIn('value="Old Publisher"', body)
        self.assertIn('value="Old Address"', body)

    @patch("app.get_book")
    def test_edit_page_returns_404_if_missing(self, mock_get_book):
        """GET /edit/<id> returns 404 when no book is found."""
        mock_get_book.return_value = None
        resp = self.client.get("/edit/999")
        self.assertEqual(resp.status_code, 404)
    
    @patch("app.update_book")
    def test_edit_post_updates_book_and_redirects(self, mock_update_book):
        """POST /edit/<id> updates the book and redirects to /citations."""
        resp = self.client.post(
            "/edit/1",
            data={
                "title": "New Title",
                "author": "New Author",
                "year": "2023",
                "publisher": "New Publisher",
                "address": "New Address",},
            follow_redirects=False,)

        mock_update_book.assert_called_once_with(
            1, "New Title", "New Author", "2023", "New Publisher", "New Address")

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers["Location"].endswith("/citations"))
