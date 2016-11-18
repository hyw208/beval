import unittest
from unittest import TestCase

from criteria import Ctx, LtE
from test_helper import acura_small


class TestLe(TestCase):

    def test_le_positive(self):
        with acura_small as acura:
            le_ = LtE("maxprice", 18.8)
            (ans, err) = le_(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

            le_ = LtE("maxprice", 18.81)
            (ans, err) = le_(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

            le_ = LtE("maxprice", 18.79)
            (ans, err) = le_(Ctx(acura))
            self.assertFalse(ans)
            self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
