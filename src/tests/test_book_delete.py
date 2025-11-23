
import os
import unittest
from unittest.mock import patch

import db_helper
from app import app
from repositories.book_repository import create_book

os.environ.setdefault("TEST_ENV", "true")


class TestBookDelete(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        # ensure reset_db runs inside the Flask application context
        self.app = app
        with self.app.app_context():
            db_helper.reset_db()

        self.client = self.app.test_client()

    @patch("app.delete_book")
    def test_delete_citation_calls_delete_and_redirects(self, mock_delete_book):
        with self.app.app_context():
            create_book(
                "Sample Title", "Sample Author", "2021", "Sample Publisher", "Sample Address"
            )

        response = self.client.get(
            "/citations/delete/1", follow_redirects=False)

        mock_delete_book.assert_called_once_with(1)

        self.assertEqual(response.status_code, 302)

    @patch("app.delete_book")
    def test_delete_nonexistent_book_calls_delete_and_redirects(self, mock_delete_book):
        # Try deleting an ID that doesn't exist; app should still call delete wrapper
        response = self.client.get(
            "/citations/delete/999", follow_redirects=False)

        mock_delete_book.assert_called_once_with(999)
        self.assertEqual(response.status_code, 302)
