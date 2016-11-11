import unittest
from criteria import Eq, cTrue, cFalse, Or, Any
from tests.test_all import BaseCriteriaTest


class TestOr(BaseCriteriaTest):

    def test_and_simple_boolean(self):
        or_ = Or(cTrue, cTrue)
        (ans, err) = or_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        any_ = Any(cTrue, cTrue)
        (ans_, err_) = any_(self.stdEmptyCtx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        or_ = Or(cTrue, cFalse)
        (ans, err) = or_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        any_ = Any(cTrue, cFalse)
        (ans_, err_) = any_(self.stdEmptyCtx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        or_ = Or(cFalse, cTrue)
        (ans, err) = or_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        any_ = Any(cFalse, cTrue)
        (ans_, err_) = any_(self.stdEmptyCtx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        or_ = Or(cFalse, cFalse)
        (ans, err) = or_(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        any_ = Any(cFalse, cFalse)
        (ans_, err_) = any_(self.stdEmptyCtx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

    def test_and_and_nesting(self):
        or_ = Or(
            Eq("last_name", "Duke"),
            Eq("first_name", "John")
        )
        or_ = Or(
            or_,
            Eq("age", 31)
        )
        or_ = Or(
            Eq("hair", "straight"),
            or_
        )
        (ans, err) = or_(self.john_duke)
        self.assertTrue(ans)
        self.assertIsNone(err)

        any_ = Any(Eq("hair", "straight"), Eq("last_name", "Duke"), Eq("first_name", "John"), Eq("age", 31))
        (ans_, err_) = any_(self.john_duke)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)


if __name__ == '__main__':
    unittest.main()
