import operator
import unittest
from unittest import TestCase

from beval.criteria import Criteria, Eq, NotEq, Ctx, Gt, to_criteria, And, All
from test_helper import acura_small, acura_midsize


class TestEq(TestCase):

    def test_eq_positive(self):
        with acura_small as acura:
            eq = Eq("make", "Acura")
            (ans, err) = eq(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

    def test_eq_negative(self):
        with acura_small as acura:
            eq = Eq("make", "acura")
            (ans, err) = eq(Ctx(acura))
            self.assertFalse(ans)
            self.assertIsNone(err)

    def test_eq_missing_attribute(self):
        with acura_small as acura:
            eq = Eq("cpu", "Intel")
            ctx = Ctx(acura, True)
            (ans, error) = eq(ctx)
            self.assertTrue(ctx.fuzzy)
            self.assertEqual(ans, Criteria.UNKNOWN)
            self.assertIsInstance(error, KeyError)

            ctx = Ctx(acura, False)
            (ans, error) = eq(ctx)
            self.assertFalse(ctx.fuzzy)
            self.assertEqual(ans, Criteria.ERROR)
            self.assertIsInstance(error, KeyError)

    def test_ser_eq(self):
        eq = Eq("make", "Acura")
        text = str(eq)
        self.assertEqual(text, "make == 'Acura'")

        eq = Eq("price", 18.8)
        text = str(eq)
        self.assertEqual(text, "price == 18.8")

        eq = Eq("american", True)
        text = str(eq)
        self.assertEqual(text, "american == True")

        and_ = And(Eq("make", "Acura"), Eq("price", 18.8))
        text = str(and_)
        self.assertEqual(text, "(make == 'Acura' and price == 18.8)")

        all_ = All(Eq("make", "Acura"), Eq("price", 18.8), Eq("american", True))
        text = str(all_)
        self.assertEqual(text, "make == 'Acura' and price == 18.8 and american == True")


class TestNotEq(TestCase):

    def test_ser_not_eq(self):
        with acura_midsize as acura:
            eq = Eq("type", "Midsize")
            (ans, err) = eq(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)
            text = str(eq)
            self.assertEqual(text, "type == 'Midsize'")

            not_eq = NotEq("type", "Midsize")
            (ans, err) = not_eq(Ctx(acura))
            self.assertFalse(ans)
            self.assertIsNone(err)
            text = str(not_eq)
            self.assertEqual(text, "type != 'Midsize'")

            not_eq = NotEq("maxprice", 19.9)
            (ans, err) = not_eq(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)
            text = str(not_eq)
            self.assertEqual(text, "maxprice != 19.9")

            not_eq = NotEq("pass", True)
            text = str(not_eq)
            self.assertEqual(text, "pass != True")


class TestGt(TestCase):

    def test_ser_gt(self):
        expected = "maxprice > 0.99"
        gt = Gt("maxprice", 0.99)
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
