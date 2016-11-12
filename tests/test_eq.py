import unittest
import operator
from criteria import Criteria, Eq, NotEq, Ctx, Gt, LtE, to_criteria
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

    def test_ser_eq(self):
        eq = Eq("name", "John")
        text = str(eq)
        self.assertEqual(text, "name == 'John'")

        eq = Eq("price", 1002)
        text = str(eq)
        self.assertEqual(text, "price == 1002")

        eq = Eq("pass", True)
        text = str(eq)
        self.assertEqual(text, "pass == True")

    def test_ser_not_eq(self):
        not_eq = NotEq("name", "John")
        text = str(not_eq)
        self.assertEqual(text, "name != 'John'")

        not_eq = NotEq("price", 1002)
        text = str(not_eq)
        self.assertEqual(text, "price != 1002")

        not_eq = NotEq("pass", True)
        text = str(not_eq)
        self.assertEqual(text, "pass != True")

    def test_ser_gt(self):
        expected = "price > 0.99"
        gt = Gt("price", 0.99)
        text = str(gt)
        self.assertEqual(expected, text)

        gt2 = to_criteria(text)
        self.assertEqual(gt.key, gt2.key)
        self.assertEqual(gt.right, gt2.right)
        self.assertEqual(gt.op, gt2.op)

    def test_ser_simple_math(self):
        expected = "100 > 99"
        gt = to_criteria(expected)
        self.assertEqual(gt.key, 100)
        self.assertEqual(gt.right, 99)
        self.assertEqual(gt.op, operator.gt)


if __name__ == '__main__':
    unittest.main()
