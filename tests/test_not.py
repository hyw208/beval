import unittest

from criteria import Eq, cTrue, cFalse, And, Not, to_criteria
from tests.test_all import BaseCriteriaTest


class TestNot(BaseCriteriaTest):

    def test_not_simple(self):
        not_ = Not(cTrue)
        (ans, err) = not_(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        not_ = Not(cFalse)
        (ans, err) = not_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_not_and(self):
        and_ = And(cTrue, cFalse)
        not_ = Not(and_)
        (ans, err) = not_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        not__ = Not(not_)
        (ans, err) = not__(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_not_eq(self):
        eq_ = Eq("last_name", "Duke")
        not_ = Not(eq_)
        (ans, err) = eq_(self.john_duke)
        self.assertTrue(ans)
        self.assertIsNone(err)

        (ans, err) = not_(self.john_duke)
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_ser_not_eq(self):
        expected = "not (last_name == 'Duke')"
        not_ = Not(Eq("last_name", "Duke"))
        text = str(not_)
        self.assertEqual(text, expected)

        not2_ = to_criteria(text)
        self.assertIsInstance(not2_, Not)
        text2 = str(not2_)
        self.assertEqual(text, text2)

        text3 = "not last_name == 'Duke'"
        not3_ = to_criteria(text3)
        text4 = str(not3_)
        self.assertNotEquals(text3, text4)
        self.assertEqual(text4, expected)

    def test_ser_not_bool(self):
        expected = "not (funny)"
        not_ = to_criteria(expected)
        text = str(not_)
        self.assertEqual(expected, text)

        text2 = "not funny"
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
        (ans, err) = not2_(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
