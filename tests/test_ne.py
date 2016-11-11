import unittest

from criteria import Criteria, NotEq
from tests.test_all import BaseCriteriaTest


class TestNe(BaseCriteriaTest):

    def test_ne_simple(self):
        ne1 = NotEq("first_name", "John")  # it means: first_name != "John"
        ne2 = NotEq("first_name", "John2")  # it means: first_name != "John2"
        ne3 = NotEq("creditCard", "AMX")  # it means: creditCard != "AMX"

        (ans, err) = ne1(self.john_duke)
        self.assertFalse(ans)
        self.assertIsNone(err)

        (ans, err) = ne2(self.john_duke)
        self.assertTrue(ans)
        self.assertIsNone(err)

        (ans, err) = ne3(self.john_duke)
        self.assertEqual(ans, Criteria.UNKNOWN)
        self.assertIsInstance(err, KeyError)


if __name__ == '__main__':
    unittest.main()
