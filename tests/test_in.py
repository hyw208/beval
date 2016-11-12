import unittest
from unittest import TestCase
from criteria import Ctx, In, to_criteria


class TestIn(TestCase):

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

if __name__ == '__main__':
    unittest.main()
