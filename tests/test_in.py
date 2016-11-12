import unittest
from unittest import TestCase
from criteria import Ctx, In, to_criteria
from tests.test_all import BaseCriteriaTest


class TestIn(BaseCriteriaTest):

    def test_in_simple(self):
        in_ = In("Rating", "BB")
        ans, err = in_(Ctx({"Rating": "BB"}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        in_ = In("Rating", "AAA", "AA", "A", "BBB", "BB", "B")
        ans, err = in_(Ctx({"Rating": "BB"}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        in_ = In("Rating", "AAA", "AA", "A")
        ans, err = in_(Ctx({"Rating": "BB"}))
        self.assertFalse(ans)
        self.assertIsNone(err)

        in_ = In("Rating", "AAA", "AA", "A")
        ans, err = in_(Ctx({"Rating": "BB"}, True))
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_ser_in(self):
        expected = "states in ('NY',)"
        in_ = to_criteria(expected)
        text = str(in_)
        self.assertEqual(expected, text)

        expected = "states in ('NY','CA',49,True,)"
        in_ = to_criteria(expected)
        text = str(in_)
        self.assertEqual(expected, text)
        ctx = Ctx({"states": 'CA'})
        (ans, err) = in_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_ser_not_in(self):
        expected = "states not in ('NY',)"
        not_in_ = to_criteria(expected)
        text = str(not_in_)
        self.assertEqual(expected, text)

        expected = "states not in ('NY','CA',49,True,)"
        not_in_ = to_criteria(expected)
        text = str(not_in_)
        self.assertEqual(expected, text)
        ctx = Ctx({"states": 'CA'})
        (ans, err) = not_in_(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_ser_simple_math(self):
        expected = "1 in (4,3,2,1,0,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, 1)
        self.assertEqual(in_.right, (4,3,2,1,0,))
        (ans, err) = in_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)

        expected = "1 in (4,3,2,0,-1,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, 1)
        self.assertEqual(in_.right, (4,3,2,0,-1,))
        (ans, err) = in_(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)

    def test_ser_simple_str(self):
        expected = "True in (False,'False',0,1,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, True)
        self.assertEqual(in_.right, (False,'False',0,1,))
        (ans, err) = in_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)


if __name__ == '__main__':
    unittest.main()
