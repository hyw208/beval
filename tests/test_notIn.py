import unittest
from unittest import TestCase
from criteria import Ctx, NotIn


class TestNotIn(TestCase):

    def test_in_simple(self):
        not_in_ = NotIn("Rating", "BB")
        (ans, err) = not_in_(Ctx({"Rating": "BB"}))
        self.assertFalse(ans)
        self.assertIsNone(err)

        not_in_ = NotIn("Rating", "AAA", "AA", "A", "BBB", "BB", "B")
        (ans, err) = not_in_(Ctx({"Rating": "BB"}))
        self.assertFalse(ans)
        self.assertIsNone(err)

        not_in_ = NotIn("Rating", "AAA", "AA", "A")
        (ans, err) = not_in_(Ctx({"Rating": "BB"}))
        self.assertTrue(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
