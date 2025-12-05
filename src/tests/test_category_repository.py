import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import repositories.category_repository as repo


class TestCategoryRepository(unittest.TestCase):
    @patch("repositories.category_repository.db")
    def test_get_categories_returns_list(self, mock_db):
        rows = [
            SimpleNamespace(id=1, name="alpha"),
            SimpleNamespace(id=2, name="beta"),
        ]

        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        cats = repo.get_categories()
        self.assertEqual(len(cats), 2)
        self.assertEqual(cats[0].id, 1)
        self.assertEqual(cats[0].name, "alpha")

        mock_db.session.execute.assert_called_once()
        sql = mock_db.session.execute.call_args[0][0]
        self.assertIn("FROM categories", str(sql))

    @patch("repositories.category_repository.db")
    def test_get_categories_empty(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        cats = repo.get_categories()
        self.assertEqual(cats, [])

    @patch("repositories.category_repository.db")
    def test_get_tags_returns_list(self, mock_db):
        rows = [
            SimpleNamespace(id=1, name="t1"),
            SimpleNamespace(id=2, name="t2"),
        ]

        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_db.session.execute.return_value = mock_result

        tags = repo.get_tags()
        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[1].name, "t2")

        mock_db.session.execute.assert_called_once()
        sql = mock_db.session.execute.call_args[0][0]
        self.assertIn("FROM tags", str(sql))

    @patch("repositories.category_repository.db")
    def test_get_tags_empty(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db.session.execute.return_value = mock_result

        tags = repo.get_tags()
        self.assertEqual(tags, [])

    @patch("repositories.category_repository.db")
    def test_get_category_by_id_found(self, mock_db):
        mock_row = SimpleNamespace(id=5, name="mycat")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        c = repo.get_category(5)
        self.assertIsNotNone(c)
        if not c:
            self.fail("Category should not be None")

        self.assertEqual(c.id, 5)
        self.assertEqual(c.name, "mycat")

        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertIn("WHERE id = :category_id", str(sql))
        self.assertEqual(params["category_id"], 5)

    @patch("repositories.category_repository.db")
    def test_get_category_by_id_none(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        c = repo.get_category(999)
        self.assertIsNone(c)

    @patch("repositories.category_repository.db")
    def test_get_tag_by_id_found(self, mock_db):
        mock_row = SimpleNamespace(id=8, name="taggy")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        t = repo.get_tag(8)
        self.assertIsNotNone(t)
        if not t:
            self.fail("Tag should not be None")

        self.assertEqual(t.id, 8)
        self.assertEqual(t.name, "taggy")

        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertTrue(
            ("WHERE tag_id = :tag_id" in str(sql)) or (
                "WHERE id = :tag_id" in str(sql))
        )
        self.assertEqual(params["tag_id"], 8)

    @patch("repositories.category_repository.db")
    def test_get_tag_by_id_none(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.session.execute.return_value = mock_result

        t = repo.get_tag(999)
        self.assertIsNone(t)

    @patch("repositories.category_repository.db")
    def test_create_category_inserts_and_returns(self, mock_db):
        mock_row = SimpleNamespace(id=10, name="newcat")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        c = repo.create_category("newcat")

        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

        self.assertEqual(c.id, 10)
        self.assertEqual(c.name, "newcat")

    @patch("repositories.category_repository.db")
    def test_create_tag_inserts_and_returns(self, mock_db):
        mock_row = SimpleNamespace(id=11, name="atag")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        t = repo.create_tag("atag")
        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

        self.assertEqual(t.id, 11)
        self.assertEqual(t.name, "atag")

    @patch("repositories.category_repository.db")
    def test_create_tags_creates_multiple(self, mock_db):
        names = ["a", "b"]
        mock_row1 = SimpleNamespace(id=21, name="a")
        mock_row2 = SimpleNamespace(id=22, name="b")

        mock_result = MagicMock()
        # emulate fetchone returning different rows on subsequent calls
        mock_result.fetchone.side_effect = [mock_row1, mock_row2]
        mock_db.session.execute.return_value = mock_result

        tags = repo.create_tags(names)
        mock_db.session.execute.assert_called()
        mock_db.session.commit.assert_called_once()

        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0].name, "a")
        self.assertEqual(tags[1].name, "b")

    @patch("repositories.category_repository.db")
    def test_get_or_create_category_returns_existing(self, mock_db):
        mock_row = SimpleNamespace(id=33, name="exists")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        c = repo.get_or_create_category("exists")
        self.assertEqual(c.id, 33)
        self.assertEqual(c.name, "exists")

    @patch("repositories.category_repository.db")
    def test_get_or_create_category_creates_when_missing(self, mock_db):
        mock_result = MagicMock()
        # first call returns None so it will create; second call returns created row
        mock_result.fetchone.side_effect = [
            None, SimpleNamespace(id=44, name="new")]
        mock_db.session.execute.return_value = mock_result

        # patch create_category to ensure it is called
        with patch("repositories.category_repository.create_category") as mock_create:
            mock_create.return_value = SimpleNamespace(id=44, name="new")
            c = repo.get_or_create_category("new")

        self.assertEqual(c.id, 44)

    @patch("repositories.category_repository.db")
    def test_get_or_create_tag_returns_existing(self, mock_db):
        mock_row = SimpleNamespace(id=55, name="texists")
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.session.execute.return_value = mock_result

        t = repo.get_or_create_tag("texists")
        self.assertEqual(t.id, 55)

    @patch("repositories.category_repository.db")
    def test_get_or_create_tag_creates_when_missing(self, mock_db):
        mock_result = MagicMock()
        mock_result.fetchone.side_effect = [
            None, SimpleNamespace(id=66, name="tnew")]
        mock_db.session.execute.return_value = mock_result

        with patch("repositories.category_repository.create_tag") as mock_create:
            mock_create.return_value = SimpleNamespace(id=66, name="tnew")
            t = repo.get_or_create_tag("tnew")

        self.assertEqual(t.id, 66)

    @patch("repositories.category_repository.db")
    def test_get_or_create_tags_mixes_existing_and_new(self, mock_db):
        # simulate first name exists, second does not; then create_tags returns the missing one
        def fake_execute(sql, params=None):
            mock = MagicMock()
            name = params.get("name") if params else None
            if name == "exist":
                mock.fetchone.return_value = SimpleNamespace(
                    id=77, name="exist")
            else:
                mock.fetchone.return_value = None
            return mock

        mock_db.session.execute.side_effect = fake_execute

        with patch("repositories.category_repository.create_tags") as mock_create_tags:
            mock_create_tags.return_value = [
                SimpleNamespace(id=88, name="new")]
            out = repo.get_or_create_tags(["exist", "new"])

        # order not guaranteed; check contents
        names = sorted([t.name for t in out])
        self.assertEqual(names, ["exist", "new"])

    @patch("repositories.category_repository.db")
    def test_assign_tag_to_citation_executes(self, mock_db):
        tag = SimpleNamespace(id=2, name="t")
        repo.assign_tag_to_citation(10, tag)
        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("repositories.category_repository.db")
    def test_assign_tags_to_citation_executes_multiple(self, mock_db):
        tags = [SimpleNamespace(id=3), SimpleNamespace(id=4)]
        repo.assign_tags_to_citation(11, tags)
        self.assertEqual(mock_db.session.execute.call_count, 2)
        mock_db.session.commit.assert_called_once()

    @patch("repositories.category_repository.db")
    def test_assign_category_to_citation_executes(self, mock_db):
        repo.assign_category_to_citation(12, 5)
        mock_db.session.execute.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("repositories.category_repository.db")
    def test_remove_tag_from_citation_executes(self, mock_db):
        repo.remove_tag_from_citation(7, 13)
        mock_db.session.execute.assert_called_once()
        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertIn("DELETE FROM citations_to_tags", str(sql))
        self.assertEqual(params["tag_id"], 7)
        self.assertEqual(params["citation_id"], 13)
        mock_db.session.commit.assert_called_once()

    @patch("repositories.category_repository.db")
    def test_remove_category_from_citation_executes(self, mock_db):
        repo.remove_category_from_citation(9, 14)
        mock_db.session.execute.assert_called_once()
        args = mock_db.session.execute.call_args[0]
        sql = args[0]
        params = args[1]
        self.assertIn("DELETE FROM citations_to_categories", str(sql))
        self.assertEqual(params["category_id"], 9)
        self.assertEqual(params["citation_id"], 14)
        mock_db.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
