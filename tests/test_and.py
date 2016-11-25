import unittest
from unittest import TestCase
from beval.criteria import Criteria, Const, Eq, NotEq, And, All, Ctx, cTrue, cFalse
from test_helper import acura_small as acura, CompareError


class TestAnd(TestCase):

    def test_simple_boolean(self):
        ctx = Ctx({})

        and_ = And(cTrue, cTrue)
        (obj, err) = and_(ctx)
        self.assertTrue(obj)
        self.assertIsNone(err)

        all_ = All(cTrue, cTrue)
        obj_, err_ = all_(ctx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

        and_ = And(cTrue, cFalse)
        (obj, err) = and_(ctx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        all_ = All(cTrue, cFalse)
        obj_, err_ = all_(ctx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

        and_ = And(cFalse, cTrue)
        (obj, err) = and_(ctx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        all_ = All(cFalse, cTrue)
        obj_, err_ = all_(ctx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

        and_ = And(cFalse, cFalse)
        (obj, err) = and_(ctx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        all_ = All(cFalse, cFalse)
        obj_, err_ = all_(ctx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_nesting_conditions(self):
        ctx = Ctx(acura)

        and_ = And(
            Eq("type", "Small"),
            Eq("make", "Acura")
        )
        and_ = And(
            and_,
            Eq("maxprice", 18.8)
        )
        and_ = And(
            NotEq("source", "USA"),
            and_
        )
        (obj, err) = and_(ctx)
        self.assertTrue(obj)
        self.assertIsNone(err)

        all_ = All(NotEq("source", "USA"), Eq("type", "Small"), Eq("make", "Acura"), Eq("maxprice", 18.8))
        obj_, err_ = all_(ctx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_and_nesting_err(self):
        with acura:
            acura.set_access_error("make", Exception("left first"))
            acura.set_access_error("source", KeyError("right 2nd"))
            ctx = Ctx(acura, True)

            and_ = Criteria().Eq("make", "Acura").Eq("type", "Small").And().Eq("source", "nonUSA").And().Done()
            (obj, err) = and_(ctx)
            self.assertTrue(obj)
            self.assertIsNotNone(err)
            self.assertEqual(err.message, "cannot find key 'make'")

            and_ = Criteria().Eq("source", "nonUSA").Eq("make", "Acura").Eq("type", "Small").And().And().Done()
            (obj, err) = and_(ctx)
            self.assertTrue(obj)
            self.assertIsNotNone(err)
            self.assertEqual(err.message, "cannot find key 'source'")

    def test_and_left_cmp_error(self):
        with acura:
            ctx = Ctx(acura, True)
            acura.set_compare_error("make", CompareError(Exception("left first")))
            acura.set_compare_error("source", CompareError(KeyError("right first")))
            make = ctx["make"]
            source = ctx["source"]

            (obj, err) = Eq("make", "xxx")(ctx)
            self.assertEqual(obj, Const.UNKNOWN)
            self.assertIsInstance(err, Exception)
            self.assertEqual(err.message, "left first")

            (obj, err) = Eq("source", "xxx")(ctx)
            self.assertEqual(obj, Const.UNKNOWN)
            self.assertIsInstance(err, KeyError)
            self.assertEqual(err.message, "right first")

            and_ = Criteria().Eq("make", "xxx").Eq("source", "yyy").And().Done()
            (obj, err) = and_(ctx)
            self.assertEqual(obj, Const.UNKNOWN)
            self.assertIsInstance(err, Exception)
            self.assertEqual(err.message, "left first")

        with acura:
            ctx = Ctx(acura, True)
            acura.set_compare_error("source", CompareError(KeyError("right first")))
            make = ctx["make"]
            source = ctx["source"]

            and_ = And(cTrue, Eq("source", "xxx"))
            (obj, err) = and_(ctx)
            self.assertTrue(obj)
            self.assertIsInstance(err, KeyError)
            self.assertEqual(err.message, "right first")

            ctx = Ctx(acura, False)
            and_ = And(cTrue, Eq("source", "xxx"))
            (obj, err) = and_(ctx)
            self.assertEqual(obj, Const.ERROR)
            self.assertIsInstance(err, KeyError)
            self.assertEqual(err.message, "right first")


if __name__ == '__main__':
    unittest.main()
