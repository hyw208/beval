import unittest
from unittest import TestCase
from beval.criteria import Ctx, to_criteria, Not, And, Eq, CRITERIA_CLS_MAP
from test_helper import acura_small


cTrue = CRITERIA_CLS_MAP["Bool"](True)
cFalse = CRITERIA_CLS_MAP["Bool"](False)


class TestNot(TestCase):

    def test_not_simple(self):
        not_ = Not(cTrue)
        (ans, err) = not_(Ctx({}))
        self.assertFalse(ans)
        self.assertIsNone(err)

        not_ = Not(cFalse)
        (ans, err) = not_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_not_and(self):
        and_ = And(cTrue, cFalse)
        not_ = Not(and_)
        (ans, err) = not_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        not__ = Not(not_)
        (ans, err) = not__(Ctx({}))
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_not_eq(self):
        with acura_small as acura:
            ctx = Ctx(acura)
            eq_ = Eq("make", "Acura")
            not_ = Not(eq_)

            (ans, err) = eq_(ctx)
            self.assertTrue(ans)
            self.assertIsNone(err)

            (ans, err) = not_(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)

    def test_ser_not_eq(self):
        expected = "not (make == 'Acura')"
        not_ = Not(Eq("make", "Acura"))
        text = str(not_)
        self.assertEqual(text, expected)

        not2_ = to_criteria(text)
        self.assertIsInstance(not2_, Not)
        text2 = str(not2_)
        self.assertEqual(text, text2)

        text3 = "not make == 'Acura'"
        not3_ = to_criteria(text3)
        self.assertIsInstance(not3_, Not)
        text4 = str(not3_)
        self.assertNotEquals(text3, text4)
        self.assertEqual(text4, expected)

    def test_ser_not_bool(self):
        expected = "not (active)"
        not_ = to_criteria(expected)
        text = str(not_)
        self.assertEqual(expected, text)

        text2 = "not active"
        not2_ = to_criteria(text2)
        text3 = str(not2_)
        self.assertNotEqual(text2, text3)
        self.assertEqual(text3, expected)

        expected = "not (True)"
        not_ = to_criteria(expected)
        text = str(not_)
        self.assertEqual(expected, text)

        text2 = "not True"
        not2_ = to_criteria(text2)
        text3 = str(not2_)
        self.assertNotEqual(text2, text3)
        self.assertEqual(text3, expected)

        expected = "not (1)"
        text2 = "not 1"
        not2_ = to_criteria(text2)
        text3 = str(not2_)
        self.assertNotEqual(text2, text3)
        self.assertEqual(text3, expected)
        (ans, err) = not2_(Ctx({}))
        self.assertFalse(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
