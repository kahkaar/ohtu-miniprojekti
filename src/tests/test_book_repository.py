import unittest
from unittest.mock import MagicMock, patch

import repositories.book_repository as repo


class TestBookRepository(unittest.TestCase):
    @patch("repositories.book_repository.db")
    def test_get_books_returns_books_list(self, mock_db):
        # Arrange: two rows returned from the database
        rows = [
            (1, "Title1", "Author1", 2000, "Pub1", "Addr1"),
            (2, "Title2", "Author2", 2010, "Pub2", "Addr2"),
        ]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        # Act
        books = repo.get_books()

        # Assert
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].title, "Title1")
        self.assertEqual(books[1].author, "Author2")

    @patch("repositories.book_repository.db")
    def test_get_book_returns_none_when_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        book = repo.get_book(123)
        self.assertIsNone(book)

    @patch("repositories.book_repository.db")
    def test_get_book_returns_book_object(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (5, "T", "A", 1999, "P", "Addr")
        mock_db.session.execute.return_value = mock_result

        book = repo.get_book(5)
        self.assertIsNotNone(book)
        self.assertEqual(book.id, 5)
        self.assertEqual(book.title, "T")

    @patch("repositories.book_repository.db")
    def test_create_book_executes_and_commits(self, mock_db):
        # Act
        repo.create_book("T", "A", 2001, "P", "Addr")

        # Assert: execute and commit called
        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("repositories.book_repository.db")
    def test_update_book_executes_and_commits(self, mock_db):
        repo.update_book(7, "T2", "A2", 2015, "P2", "Addr2")

        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
