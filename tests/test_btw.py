import operator
import unittest
from unittest import TestCase

from beval.criteria import Criteria, Ctx, Between, to_criteria
from test_helper import acura_small


class TestBetween(TestCase):

    def test_btw_simple(self):
        with acura_small as acura:
            ctx = Ctx(acura)

            btw_ = Between(18.7, "maxprice", 18.9)
            (ans, err) = btw_(ctx)
            self.assertTrue(ans)
            self.assertIsNone(err)

            btw_ = Between(18.8, "maxprice", 18.9)
            (ans, err) = btw_(ctx)
            self.assertTrue(ans)
            self.assertIsNone(err)

            btw_ = Between(18.9, "maxprice", 19.0)
            (ans, err) = btw_(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)

            btw_ = Between(18.7, "maxprice", 18.8)
            (ans, err) = btw_(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)

    def test_missing_info(self):
        for ctx, expected in [(Ctx({}, False), Criteria.ERROR), (Ctx({}, True), Criteria.UNKNOWN)]:
            btw_ = Between(10, "price", 20)
            (ans, err) = btw_(ctx)
            self.assertEqual(ans, expected)
            self.assertIsInstance(err, KeyError)

    def test_ser(self):
        expected = "234 < score <= 456"
        btw = to_criteria(expected)
        self.assertIsInstance(btw, Between)
        self.assertEqual(btw.lower, 234)
        self.assertEqual(btw.lower_op, operator.lt)
        self.assertEqual(btw.key, "score")
        self.assertEqual(btw.upper_op, operator.le)
        self.assertEqual(btw.upper, 456)
        text = str(btw)
        self.assertEqual(expected, text)

    def test_no_key(self):
        ctx = Ctx({})

        expected = "1 <= 2 < 3"
        btw = to_criteria(expected)
        text = str(btw)
        self.assertEqual(expected, text)
        (ans, err) = btw(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        expected = "3 <= 3 < 3"
        btw = to_criteria(expected)
        text = str(btw)
        self.assertEqual(expected, text)
        (ans, err) = btw(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
