import unittest
from unittest import TestCase
from criteria import Ctx, In


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


if __name__ == '__main__':
    unittest.main()
