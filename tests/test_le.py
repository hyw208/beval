import unittest
from unittest import TestCase

from criteria import Ctx, LtE


class TestLe(TestCase):

    def test_le_positive(self):
        le_ = LtE("price", 99.99)

        ctx = Ctx({"price": 99.98})
        ans, err = le_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        ctx = Ctx({"price": 99.99})
        ans, err = le_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        ctx = Ctx({"price": 99.999})
        ans, err = le_(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
