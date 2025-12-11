
import unittest
from typing import cast
from unittest.mock import Mock, patch

import requests
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

    def test_get_posted_fields_filters_and_sanitizes(self):
        form = {
            "title": "  A  title ",
            "citation_key": " should-be-ignored",
            "entry_type": "book",
            "author": " John   Doe ",
            "empty": "   ",
        }

        posted = util.extract_fields(form)

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

    def test_parse_search_queries_from_util(self):
        args = {
            "q": "  spaced out  ",
            "citation_key": " AbC123 ",
            "author": " John Doe ",
            "year_from": "1990",
            "year_to": "1999",
            "sort_by": "citation_key",
            "direction": "Down",
        }

        parsed = util.parse_search_queries(args)

        self.assertEqual(parsed["q"], "spaced out")
        self.assertEqual(parsed["citation_key"], "abc123")
        self.assertEqual(parsed["author"], "john doe")
        self.assertEqual(parsed["year_from"], 1990)
        self.assertEqual(parsed["year_to"], 1999)
        self.assertEqual(parsed["sort_by"], "citation_key")

        self.assertIn(parsed["direction"], ("ASC", "DESC"))

    def test_parse_search_queries_edge_cases(self):
        parsed = util.parse_search_queries({})
        self.assertIsNone(parsed["sort_by"])
        self.assertEqual(parsed["direction"], "ASC")

        parsed = util.parse_search_queries({"year_from": "abc", "year_to": ""})
        self.assertIsNone(parsed["year_from"])
        self.assertIsNone(parsed["year_to"])

    def test_parse_search_queries_int_years_and_variants(self):
        args = {"year_from": 2015, "year_to": 2020,
                "sort_by": "Year", "direction": "desc"}
        parsed = util.parse_search_queries(args)
        self.assertEqual(parsed["year_from"], 2015)
        self.assertEqual(parsed["year_to"], 2020)
        self.assertEqual(parsed["sort_by"], "year")
        self.assertEqual(parsed["direction"], "DESC")

    def test_parse_search_queries_invalid_direction_and_blank_fields(self):
        args = {"direction": "down", "citation_key": "   ",
                "author": None, "q": "\n  "}
        parsed = util.parse_search_queries(args)
        self.assertEqual(parsed["direction"], "ASC")
        self.assertEqual(parsed["citation_key"], "")
        self.assertEqual(parsed["author"], "")
        self.assertEqual(parsed["q"], "")

    def test_parse_search_queries_handles_str_exception_in_year(self):
        class BadStr:
            def __str__(self):
                raise TypeError("bad to-string")

        parsed = util.parse_search_queries(
            {"year_from": BadStr(), "year_to": BadStr()})
        self.assertIsNone(parsed["year_from"])
        self.assertIsNone(parsed["year_to"])


class TestUtilExtensions(unittest.TestCase):
    def test_parse_entry_type_and_conversions(self):
        self.assertIsNone(util.parse_entry_type(None))

        parsed = util.parse_entry_type({"id": 7, "name": "misc"})
        self.assertIsNotNone(parsed)

        # # UNNECESSARY. Here to satisfy type checker...
        if not parsed:
            self.fail("Parsed EntryType should not be None")

        self.assertEqual(parsed.id, 7)
        self.assertEqual(parsed.name, "misc")

    def test_to_category_and_to_tag_and_to_citation_json_variants(self):
        row_cat = type("R", (), {"id": 1, "name": "C1"})
        cat = util.to_category(row_cat)
        self.assertEqual(cat.id, 1)
        self.assertEqual(cat.name, "C1")

        row_tag = type("R", (), {"id": 2, "name": "T1"})
        tag = util.to_tag(row_tag)
        self.assertEqual(tag.id, 2)
        self.assertEqual(tag.name, "T1")

        row = type("R", (), {"id": 3, "entry_type": "book",
                   "citation_key": "k3", "fields": {"a": 1}})
        c = util.to_citation(row)

        if not c:
            self.fail("Citation should not be None")
        self.assertEqual(c.fields, {"a": 1})

        row2 = type("R", (), {"id": 4, "entry_type": "book",
                    "citation_key": "k4", "fields": '{"a":2}'})
        c2 = util.to_citation(row2)

        if not c2:
            self.fail("Citation should not be None")
        self.assertEqual(c2.fields, {"a": 2})

        row3 = type("R", (), {"id": 5, "entry_type": "book",
                    "citation_key": "k5", "fields": 'not json'})
        c3 = util.to_citation(row3)

        # # UNNECESSARY. Here to satisfy type checker...
        if not c3:
            self.fail("Citation should not be None")
        self.assertEqual(c3.fields, {})

    def test_collapse_and_hyphens_and_none_citation(self):
        self.assertEqual(util.collapse_to_hyphens(" A B C "), "A-B-C")

        self.assertEqual(util.collapse_to_hyphens(123), 123)

    def test_to_citation_none(self):
        self.assertIsNone(util.to_citation(None))

    def test_to_entry_type_none_handling(self):
        row = type("R", (), {"id": 9, "name": "custom"})
        et = util.to_entry_type(row)
        self.assertEqual(et.id, 9)
        self.assertEqual(et.name, "custom")


class TestUtilTagsExtra(unittest.TestCase):
    def test_extract_tags_with_tags_new_and_dedup(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        # existing tags a,b and new tags 'b, c, , a' should produce ['a','b','c']
        f = DummyForm({"tag_list": ["a", "b"], "new_tags": "b, c, , a "})
        out = util.extract_metadata(f).get("tags", [])
        self.assertEqual(out, ["a", "b", "c"])

    def test_extract_tags_blank_and_missing(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        # no tags present
        f_empty = DummyForm({})
        self.assertEqual(util.extract_metadata(f_empty).get("tags", []), [])

        # new_tags provided but only whitespace -> should be ignored
        f_blank_new = DummyForm({"new_tags": "   ,  ,\t"})
        self.assertEqual(util.extract_metadata(
            f_blank_new).get("tags", []), [])


class TestToCitationVariants(unittest.TestCase):
    def test_to_citation_with_dict_fields_and_list_tags(self):
        row = type("R", (), {
            "id": 10,
            "entry_type": "article",
            "citation_key": "k10",
            "fields": {"a": 1},
            "tags": ["t1", "t2"],
            "categories": ["c1"],
        })
        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.fields, {"a": 1})
        self.assertEqual(c.tags, ["t1", "t2"])
        self.assertEqual(c.categories, ["c1"])

    def test_to_citation_with_json_string_fields_and_json_tags(self):
        row = type("R", (), {
            "id": 11,
            "entry_type": "book",
            "citation_key": "k11",
            "fields": '{"b":2}',
            "tags": '["x","y"]',
            "categories": '["catA"]',
        })
        c = util.to_citation(row)
        self.assertEqual(c.fields, {"b": 2})
        self.assertEqual(c.tags, ["x", "y"])
        self.assertEqual(c.categories, ["catA"])

    def test_to_citation_with_comma_separated_tags_and_categories(self):
        row = type("R", (), {
            "id": 12,
            "entry_type": "misc",
            "citation_key": "k12",
            "fields": '{}',
            "tags": 'a, b, , c',
            "categories": ' c1, c2 ',
        })
        c = util.to_citation(row)
        self.assertEqual(c.tags, ["a", "b", "c"])
        self.assertEqual(c.categories, ["c1", "c2"])

    def test_to_citation_with_none_tags_and_categories(self):
        row = type("R", (), {
            "id": 13,
            "entry_type": "misc",
            "citation_key": "k13",
            "fields": None,
            "tags": None,
            "categories": None,
        })
        c = util.to_citation(row)
        self.assertEqual(c.fields, {})
        self.assertEqual(c.tags, [])
        self.assertEqual(c.categories, [])

    def test_to_citation_with_unexpected_iterable(self):
        class IterableLike:
            def __iter__(self):
                yield 'i1'
                yield 'i2'

        row = type("R", (), {
            "id": 14,
            "entry_type": "misc",
            "citation_key": "k14",
            "fields": {},
            "tags": IterableLike(),
            "categories": IterableLike(),
        })
        c = util.to_citation(row)

        if not c:
            self.fail("to_citation returned None unexpectedly.")

        self.assertEqual(c.tags, ['i1', 'i2'])
        self.assertEqual(c.categories, ['i1', 'i2'])

    def test_to_citation_with_non_iterable_truthy_triggers_typeerror(self):
        # An object that is truthy but not iterable should cause list(obj)
        # to raise TypeError and _to_list should return an empty list.
        class NotIterable:
            pass

        row = type("R", (), {
            "id": 15,
            "entry_type": "misc",
            "citation_key": "k15",
            "fields": {},
            "tags": NotIterable(),
            "categories": NotIterable(),
        })

        c = util.to_citation(row)

        if not c:
            self.fail("to_citation returned None unexpectedly.")

        self.assertEqual(c.tags, [])
        self.assertEqual(c.categories, [])

    def test_to_citation_with_json_array_string_fields_returns_original_string(self):
        # fields is a JSON array string; parse yields a list (not dict), so _parse_fields returns original string
        row = type("R", (), {
            "id": 16,
            "entry_type": "misc",
            "citation_key": "k16",
            "fields": '["x","y"]',
            "tags": None,
            "categories": None,
        })

        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.fields, '["x","y"]')

    def test_to_citation_with_list_fields_returns_list(self):
        # fields provided as a list should be returned as-is
        row = type("R", (), {
            "id": 17,
            "entry_type": "misc",
            "citation_key": "k17",
            "fields": ['f1', 'f2'],
            "tags": None,
            "categories": None,
        })

        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.fields, ['f1', 'f2'])

    def test_to_citation_handles_missing_tags_and_categories_attributes(self):
        # row has no tags or categories attributes at all
        row = type("R", (), {
            "id": 18,
            "entry_type": "book",
            "citation_key": "k18",
            "fields": {},
        })

        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.tags, [])
        self.assertEqual(c.categories, [])

    def test_to_citation_with_tuple_tags_and_categories(self):
        # tags and categories provided as tuple should be converted to lists
        row = type("R", (), {
            "id": 19,
            "entry_type": "misc",
            "citation_key": "k19",
            "fields": {},
            "tags": ('ta', 'tb'),
            "categories": ('ca',),
        })

        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.tags, ['ta', 'tb'])
        self.assertEqual(c.categories, ['ca'])

    def test_to_citation_json_array_string_tags_triggers_parsed_list_branch(self):
        # Ensure that when tags/categories are JSON array strings, _to_list uses parsed list
        row = type("R", (), {
            "id": 20,
            "entry_type": "misc",
            "citation_key": "k20",
            "fields": {},
            "tags": '["tagA","tagB"]',
            "categories": '["catX"]',
        })

        c = util.to_citation(row)
        self.assertIsNotNone(c)
        self.assertEqual(c.tags, ['tagA', 'tagB'])
        self.assertEqual(c.categories, ['catX'])


class TestDOIHelpers(unittest.TestCase):
    def test__doi_extract_no_match(self):
        self.assertIsNone(util._doi_extract('no doi here'))

    def test__doi_extract_with_url_and_trailing_dot(self):
        v = 'https://doi.org/10.1234/abcd.'
        self.assertEqual(util._doi_extract(v), '10.1234/abcd')

    def test__doi_first_of_keys_list_and_scalar(self):
        d = {'a': ['x'], 'b': 'y'}
        self.assertEqual(util._doi_first_of_keys(d, ('a', 'b')), 'x')
        d2 = {'a': [], 'b': 'y'}
        self.assertEqual(util._doi_first_of_keys(d2, ('a', 'b')), 'y')
        d3 = {}
        self.assertIsNone(util._doi_first_of_keys(d3, ('a', 'b')))

    def test__doi_parse_authors_variants(self):
        authors = [
            {'given': 'John', 'family': 'Doe'},
            {'literal': 'SingleName'},
            {'family': 'Smith'},
            'Anonymous'
        ]
        self.assertEqual(util._doi_parse_authors(authors),
                         'John Doe; SingleName; Smith; Anonymous')
        self.assertIsNone(util._doi_parse_authors('notalist'))

    def test__doi_parse_authors_empty_list(self):
        # empty list should return None
        self.assertIsNone(util._doi_parse_authors([]))

    def test__doi_parse_authors_family_only(self):
        # dict with only family should return the family name
        authors = [{'family': 'OnlyFamily'}]
        self.assertEqual(util._doi_parse_authors(authors), 'OnlyFamily')

    def test__doi_parse_authors_plain_string(self):
        # single-string author should be returned as-is
        authors = ["JustName"]
        result = util._doi_parse_authors(authors)
        self.assertEqual(result, "JustName")

    def test__doi_parse_authors_with_non_dict_or_str(self):
        # single-string author should be returned as-is
        authors = ["JustName", 1]
        result = util._doi_parse_authors(authors)
        self.assertEqual(result, "JustName")

    def test__doi_parse_authors_exhaustive(self):
        # ensure every inner branch is exercised
        cases = [
            ({'given': 'G', 'family': 'F'}, 'G F'),
            ({'literal': 'L'}, 'L'),
            ({'family': 'OnlyF'}, 'OnlyF'),
            ({'given': 'OnlyG'}, None),  # given only -> nothing appended
            ('PlainString', 'PlainString'),
        ]

        for inp, expected in cases:
            if isinstance(inp, str):
                res = util._doi_parse_authors([inp])
            else:
                res = util._doi_parse_authors([inp])

            if expected is None:
                self.assertIsNone(res)
            else:
                self.assertEqual(res, expected)

    def test__doi_parse_authors_mixed_and_tuple(self):
        # mixed list: dict then string should include both parts
        authors = [{'given': 'A', 'family': 'B'}, 'Cname']
        self.assertEqual(util._doi_parse_authors(authors), 'A B; Cname')

        # tuple input should also be accepted and string branch hit
        authors_tuple = ({'family': 'Solo'}, 'Plain')
        self.assertEqual(util._doi_parse_authors(authors_tuple), 'Solo; Plain')

    def test__doi_parse_authors_all_combinations(self):
        # Exhaustively test presence/absence of given/family/literal
        for given_present in (False, True):
            for family_present in (False, True):
                for literal_present in (False, True):
                    d = {}
                    if given_present:
                        d['given'] = 'G'
                    if family_present:
                        d['family'] = 'F'
                    if literal_present:
                        d['literal'] = 'L'

                    # Expected selection logic: given+family > literal > family > None
                    if given_present and family_present:
                        expected = 'G F'
                    elif literal_present:
                        expected = 'L'
                    elif family_present:
                        expected = 'F'
                    else:
                        expected = None

                    res = util._doi_parse_authors([d])
                    if expected is None:
                        self.assertIsNone(res)
                    else:
                        self.assertEqual(res, expected)

    def test__doi_parse_year_variants(self):
        self.assertEqual(util._doi_parse_year(
            {'issued': {'date-parts': [[2020, 1, 2]]}}), 2020)
        # non-int first element
        self.assertIsNone(util._doi_parse_year(
            {'issued': {'date-parts': [['x']]}}))
        # missing issued
        self.assertIsNone(util._doi_parse_year({}))
        # issued not a dict -> should return None
        self.assertIsNone(util._doi_parse_year(
            {'issued': ['not', 'a', 'dict']}))

    @patch('util.requests.get')
    def test_fetch_doi_metadata_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value={
            'title': ['A Great Paper'],
            'author': [
                {'given': 'Alice', 'family': 'Adams'},
                {'literal': 'Bob B.'}
            ],
            'issued': {'date-parts': [[2010]]},
            'container-title': ['Journal of Testing'],
            'publisher': 'TestPub',
            'page': '12-34',
            'volume': 7,
            'issue': '2'
        })
        mock_get.return_value = mock_resp
        fields = util.fetch_doi_metadata('https://doi.org/10.1000/testdoi')
        self.assertIsNotNone(fields)
        self.assertIsInstance(fields, dict)
        fields = cast(dict, fields)
        self.assertEqual(fields.get('title'), 'A Great Paper')
        self.assertEqual(fields.get('author'), 'Alice Adams; Bob B.')
        self.assertEqual(fields.get('year'), 2010)
        self.assertEqual(fields.get('journaltitle'), 'Journal of Testing')
        self.assertEqual(fields.get('publisher'), 'TestPub')
        self.assertEqual(fields.get('pages'), '12-34')
        self.assertEqual(fields.get('volume'), '7')
        self.assertEqual(fields.get('number'), '2')

    @patch('util.requests.get')
    def test_fetch_doi_metadata_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException('boom')
        self.assertIsNone(util.fetch_doi_metadata('10.1000/doesntmatter'))

    @patch('util.requests.get')
    def test_fetch_doi_metadata_invalid_json(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(side_effect=ValueError('bad json'))
        mock_get.return_value = mock_resp
        self.assertIsNone(util.fetch_doi_metadata('10.1000/x'))

    @patch('util.requests.get')
    def test_fetch_doi_metadata_non_dict_json(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value=['not', 'a', 'dict'])
        mock_get.return_value = mock_resp
        self.assertIsNone(util.fetch_doi_metadata('10.1000/x'))

    def test_fetch_doi_metadata_empty_input(self):
        self.assertIsNone(util.fetch_doi_metadata(''))
        self.assertIsNone(util.fetch_doi_metadata(None))
        # input with no DOI-like substring should also return None
        self.assertIsNone(util.fetch_doi_metadata('no doi here'))

    @patch('util.requests.get')
    def test_fetch_doi_metadata_title_string_and_authors_key(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value={
            'title': 'Single title string',
            'authors': ['Solo Author'],
            'issued': {'date-parts': [[2001]]}
        })
        mock_get.return_value = mock_resp

        fields = util.fetch_doi_metadata('10.2000/titlecase')
        self.assertIsNotNone(fields)
        self.assertIsInstance(fields, dict)
        fields = cast(dict, fields)
        self.assertEqual(fields.get('title'), 'Single title string')
        self.assertEqual(fields.get('author'), 'Solo Author')

    @patch('util.requests.get')
    def test_fetch_doi_metadata_empty_dict_returns_none(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value={})
        mock_get.return_value = mock_resp

        # empty dict -> no recognized fields -> should return None
        self.assertIsNone(util.fetch_doi_metadata('10.3000/empty'))


class TestUtilMore(unittest.TestCase):
    def test_extract_fields_year_invalid_raises(self):
        # Non-digit year should raise ValueError from extract_fields
        form = {"year": "abcd", "title": "ok"}
        with self.assertRaises(ValueError):
            util.extract_fields(form)

    def test_extract_data_propagates_extract_fields_error(self):
        # extract_data should propagate ValueError raised by extract_fields
        form = {"year": "-1"}
        # '-1' is not all digits -> should raise
        with self.assertRaises(ValueError):
            util.extract_data(form)

    def test_extract_metadata_handles_getlist_none_and_dedup(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            # Simulate getlist returning None (should be treated as empty)
            def getlist(self, k):
                return None

        f = DummyForm({"new_tags": "a, b, a", "new_categories": "c, c"})
        meta = util.extract_metadata(f)
        self.assertEqual(meta.get("tags"), ["a", "b"])
        self.assertEqual(meta.get("categories"), ["c"])

    def test_extract_citation_key_empty_raises(self):
        self.assertRaises(ValueError, lambda: util.extract_citation_key({}))

    def test__doi_parse_year_date_parts_alt_key(self):
        # support for 'date_parts' key should be handled the same
        d = {"issued": {"date_parts": [[1984, 5, 6]]}}
        self.assertEqual(util._doi_parse_year(d), 1984)


class TestUtilExtra(unittest.TestCase):
    def test_extract_fields_ignores_disallowed_and_handles_year_bounds(self):
        # disallowed keys should be filtered out
        form = {
            'title': '  Title  ',
            'citation_key': 'should-be-ignored',
            'entry_type': 'book',
            'year': '0',
        }
        out = util.extract_fields(form)
        self.assertIn('title', out)
        self.assertNotIn('citation_key', out)
        self.assertNotIn('entry_type', out)
        # year at lower bound passes
        self.assertEqual(out.get('year'), '0')

        # year at upper bound passes
        form['year'] = '9999'
        out2 = util.extract_fields(form)
        self.assertEqual(out2.get('year'), '9999')

    def test_extract_fields_rejects_out_of_range_year(self):
        form = {'year': '10000', 'title': 'ok'}
        with self.assertRaises(ValueError):
            util.extract_fields(form)

    def test_extract_data_success_path_and_metadata_integration(self):
        # create a form-like object that supports items(), get(), getlist()
        class FormLike:
            def __init__(self, items):
                self._items = items

            def items(self):
                return list(self._items.items())

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        f = FormLike({
            'title': '  My Title ',
            'year': '2020',
            'tag_list': ['a', 'b'],
            'new_tags': 'b, c, ',
            'category_list': [],
            'new_categories': 'x, x , y'
        })

        fields, cats, tags = util.extract_data(f)
        # fields come from extract_fields
        self.assertEqual(fields.get('title'), 'My Title')
        self.assertEqual(fields.get('year'), '2020')
        # categories and tags are deduped and sanitized
        self.assertEqual(tags, ['a', 'b', 'c'])
        self.assertEqual(cats, ['x', 'y'])

    def test_extract_metadata_existing_and_new_values_and_getlist_none(self):
        # test with getlist present and with getlist returning None
        class F:
            def __init__(self, items):
                self._items = items

            def getlist(self, k):
                return self._items.get(k)

            def get(self, k, default=None):
                return self._items.get(k, default)

        # case: getlist returns explicit list
        f1 = F({'tag_list': [' t1 ', 't2'], 'new_tags': 't2, t3',
                'category_list': ['c1'], 'new_categories': ''})
        meta1 = util.extract_metadata(f1)
        self.assertEqual(meta1['tags'], ['t1', 't2', 't3'])
        self.assertEqual(meta1['categories'], ['c1'])

        # case: getlist returns None -> should be treated as empty
        f2 = F({'tag_list': None, 'new_tags': 'a, a, b',
               'category_list': None, 'new_categories': None})
        meta2 = util.extract_metadata(f2)
        self.assertEqual(meta2['tags'], ['a', 'b'])
        self.assertEqual(meta2['categories'], [])

    def test_extract_citation_key_success_and_failure(self):
        good = {'citation_key': '  My Key  '}
        self.assertEqual(util.extract_citation_key(good), 'My-Key')

        bad = {'citation_key': '   '}
        with self.assertRaises(ValueError):
            util.extract_citation_key(bad)

    def test_extract_metadata_with_an_empty_str_as_tag(self):
        class DummyForm:
            def __init__(self, items):
                self._items = items

            def get(self, k, default=None):
                return self._items.get(k, default)

            def getlist(self, k):
                return self._items.get(k, [])

        f = DummyForm({"tag_list": ["a", ""], "new_tags": " , b "})
        out = util.extract_metadata(f)
        self.assertEqual(out.get("tags"), ["a", "b"])

    def test_parse_search_queries_with_str_tags_cats(self):
        args = {
            "tag_list": " tag1 ",
            "category_list": " catA ",
        }

        parsed = util.parse_search_queries(args)

        self.assertEqual(parsed["tags"], ["tag1"])
        self.assertEqual(parsed["categories"], ["catA"])


if __name__ == "__main__":
    unittest.main()
