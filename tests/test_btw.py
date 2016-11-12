import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, LtE, Lt, Between, to_criteria
from tests.test_all import BaseCriteriaTest


class TestBetween(BaseCriteriaTest):

    def test_btw_simple(self):
        btw_ = Between(100, "price", 200)  # 100 <= price < 200
        ans, err = btw_(self.stdCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        btw_ = Between(99, "price", 101)  # 99 <= price < 101
        ans, err = btw_(self.stdCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        btw_ = Between(101, "price", 200)  # 101 <= price < 200
        ans, err = btw_(self.stdCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        btw_ = Between(60, "price", 100)  # 60 <= price < 100
        ans, err = btw_(self.stdCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_missing_info_fuzzy_off(self):
        btw_ = Between(100, "price", 200)  # 100 <= price < 200
        ans, err = btw_(self.stdEmptyCtx)
        self.assertEqual(ans, Criteria.ERROR)
        self.assertIsInstance(err, KeyError)

    def test_fuzzy_on(self):
        btw_ = Between(100, "price", 200)  # 100 <= price < 200
        ans, err = btw_(self.fuzzyEmptyCtx)
        self.assertEqual(ans, Criteria.UNKNOWN)
        self.assertIsInstance(err, KeyError)

    def test_ser(self):
        expected = "234 < score <= 456"
        btw = to_criteria(expected)
        text = str(btw)
        self.assertEqual(expected, text)

    def test_no_key(self):
        expected = "1 <= 2 < 3"
        btw = to_criteria(expected)
        text = str(btw)
        self.assertEqual(expected, text)
        (ans, err) = btw(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        expected = "3 <= 3 < 3"
        btw = to_criteria(expected)
        text = str(btw)
        self.assertEqual(expected, text)
        (ans, err) = btw(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
