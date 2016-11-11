import unittest

from criteria import Criteria, Eq, Ctx
from tests.test_all import BaseCriteriaTest


class TestEq(BaseCriteriaTest):

    def test_eq_positive(self):
        eq = Eq("first_name", "John")
        (ans, err) = eq(self.john_duke)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_eq_negative(self):
        eq = Eq("first_name", "Paul")
        (ans, err) = eq(self.john_duke)
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_eq_unknown_fuzzy_true(self):
        eq = Eq("middle_name", "Joe")
        (ans, error) = eq(self.john_duke)
        self.assertTrue(self.john_duke.fuzzy)
        self.assertEqual(ans, Criteria.UNKNOWN)
        self.assertIsInstance(error, KeyError)

    def test_eq_unknown_fuzzy_false(self):
        eq = Eq("middle_name", "Joe")
        john_duke_copy = Ctx( self.john_duke.one, False)
        ans, error = eq(john_duke_copy)
        self.assertEqual(ans, Criteria.ERROR)
        self.assertIsInstance(error, KeyError)

    def test_ser(self):
        eq = Eq("name", "John")
        text = str(eq)
        self.assertEqual(text, "name == 'John'")

        eq = Eq("price", 1002)
        text = str(eq)
        self.assertEqual(text, "price == 1002")

        eq = Eq("pass", True)
        text = str(eq)
        self.assertEqual(text, "pass == True")


if __name__ == '__main__':
    unittest.main()
