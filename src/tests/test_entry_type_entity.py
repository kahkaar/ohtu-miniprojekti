import unittest

from entities.entry_type import EntryType


class TestEntryTypeEntity(unittest.TestCase):
    def test_to_dict_and_str_and_repr(self):
        et = EntryType(5, "conference")
        d = et.to_dict()
        self.assertEqual(d["id"], 5)
        self.assertEqual(d["name"], "conference")

        self.assertEqual(str(et), "conference")
        r = repr(et)
        self.assertIn("conference", r)


if __name__ == "__main__":
    unittest.main()
