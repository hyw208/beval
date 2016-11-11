import unittest
from criteria import Criteria, Eq, NotEq, And, All, cTrue, cFalse
from tests.test_all import BaseCriteriaTest


class TestAnd(BaseCriteriaTest):

    def test_and_simple_boolean(self):
        and_ = And(cTrue, cTrue)
        (obj, err) = and_(self.stdCtx)
        self.assertTrue(obj)
        self.assertIsNone(err)

        all_ = All(cTrue, cTrue)
        obj_, err_ = all_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

        and_ = And(cTrue, cFalse)
        (obj, err) = and_(self.stdCtx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        all_ = All(cTrue, cFalse)
        obj_, err_ = all_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

        and_ = And(cFalse, cTrue)
        (obj, err) = and_(self.stdCtx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        all_ = All(cFalse, cTrue)
        obj_, err_ = all_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

        and_ = And(cFalse, cFalse)
        (obj, err) = and_(self.stdCtx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        all_ = All(cFalse, cFalse)
        obj_, err_ = all_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_and_and_nesting(self):
        and_ = And(
            Eq("last_name", "Duke"),
            Eq("first_name", "John")
        )
        and_ = And(
            and_,
            Eq("age", 31)
        )
        and_ = And(
            NotEq("hair", "straight"),
            and_
        )
        (obj, err) = and_(self.john_duke)
        self.assertTrue(obj)
        self.assertIsNone(err)

        all_ = All(NotEq("hair", "straight"), Eq("last_name", "Duke"), Eq("first_name", "John"), Eq("age", 31))
        obj_, err_ = all_(self.john_duke)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_and_nesting_err(self):
        and_ = And(self.true_key_error_lf, self.true_key_error_rf)
        and_ = And(and_, self.true_key_error_r2nd)
        (obj, err) = and_(self.stdCtx)
        self.assertTrue(obj)
        self.assertIsNotNone(err)
        self.assertEqual(err.message, "left first")

        and_ = And(self.true_key_error_lf, self.true_key_error_rf)
        and_ = And(self.true_key_error_r2nd, and_)
        (obj, err) = and_(self.stdCtx)
        self.assertTrue(obj)
        self.assertIsNotNone(err)
        self.assertEqual(err.message, "left 2nd")

    def test_and_left_true(self):
        # left.true, right.true
        and_ = And(self.true_key_error_lf, self.true_key_error_rf)
        (obj, err) = and_(self.stdCtx)
        self.assertTrue(obj)
        self.assertIsNotNone(err)
        self.assertEqual(err.message, "left first")

        # left.true, right.error, fuzzy.true
        and_ = And(cTrue, self.true_key_error_rf)
        (obj, err) = and_(self.fuzzyCtx)
        self.assertTrue(obj)
        self.assertIsNotNone(err)
        self.assertEqual(err.message, "right first")

        # left.true, right.error, fuzzy.false
        and_ = And(cTrue, self.none_error_rf)
        (obj, err) = and_(self.stdCtx)
        self.assertEqual(obj, Criteria.ERROR)
        self.assertIsNotNone(err)
        self.assertEqual(err.message, "right first")

        # left.true, right.unknown, fuzzy.true
        and_ = And(cTrue, self.unknown_none)
        (obj, err) = and_(self.fuzzyCtx)
        self.assertTrue(obj)
        self.assertIsNone(err)

        # left.true, right.unknown, fuzzy.false
        and_ = And(cTrue, self.unknown_none)
        (obj, err) = and_(self.stdCtx)
        self.assertEqual(obj, Criteria.ERROR)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
