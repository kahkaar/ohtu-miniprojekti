import unittest

from entities.category import Category, Tag


class TestCategoryEntity(unittest.TestCase):
    def test_category_properties_and_repr(self):
        c = Category(2, "Science")
        self.assertEqual(c.id, 2)
        self.assertEqual(c.name, "Science")

        d = c.to_dict()
        self.assertEqual(d, {"id": 2, "name": "Science"})

        # __str__ should return the name
        self.assertEqual(str(c), "Science")

        # repr should include the class name and values
        r = repr(c)
        self.assertIn("Science", r)

    def test_tag_is_subclass_and_works(self):
        t = Tag(7, "taggy")
        # Tag inherits Category behavior
        self.assertEqual(t.id, 7)
        self.assertEqual(t.name, "taggy")
        self.assertIsInstance(t, Category)


if __name__ == "__main__":
    unittest.main()
