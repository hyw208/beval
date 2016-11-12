import unittest
from unittest import TestCase

from criteria import Criteria, Ctx, Between, All, And, to_criteria
from tests.test_helper import MockCriteria


class BaseCriteriaTest(TestCase):

    def setUp(self):
        self.target = {"price": 100}
        self.stdCtx = Ctx(self.target)
        self.fuzzyCtx = Ctx(self.target, fuzzy=True)
        self.stdEmptyCtx = Ctx({})
        self.fuzzyEmptyCtx = Ctx({}, fuzzy=True)
        self.john_duke = Ctx(
            {"first_name": "John", "last_name": "Duke", "address": "New York, NY", "age": 31, "hair": "curly"},
            True
        )

        self.price_btw_100_200 = Between(100, "price", 200)
        self.price_btw_99_101 = Between(99, "price", 101)
        self.price_btw_50_101 = Between(50, "price", 101)
        self.price_btw_98_99 = Between(98, "price", 99)

        self.unknown_exception = MockCriteria(Criteria.UNKNOWN, Exception("Address not found"))
        self.unknown_error = MockCriteria(Criteria.UNKNOWN, KeyError("Address not found"))
        self.unknown_none = MockCriteria(Criteria.UNKNOWN, None)
        self.error_error = MockCriteria(Criteria.ERROR, KeyError("Address not found"))
        self.none_error = MockCriteria(None, KeyError("Address not found"))
        self.none_error_rf = MockCriteria(None, KeyError("right first"))
        self.true_key_error_lf = MockCriteria(True, KeyError("left first"))
        self.true_key_error_rf = MockCriteria(True, KeyError("right first"))
        self.true_key_error_r2nd = MockCriteria(True, KeyError("left 2nd"))


class TestAll(BaseCriteriaTest):

    def test_all_positive(self):
        many = [self.price_btw_100_200, self.price_btw_99_101, self.price_btw_50_101]
        all_ = All(*many)
        (obj, err) = all_(self.stdCtx)
        self.assertTrue(obj)
        self.assertIsNone(err)

        """ test consistent behavior between All, And """
        and_ = And(And(many[0], many[1]), many[2])
        (obj_, err_) = and_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_all_negative(self):
        many = [self.price_btw_100_200, self.price_btw_98_99, self.price_btw_50_101]
        all_ = All(*many)
        (obj, err) = all_(self.stdCtx)
        self.assertFalse(obj)
        self.assertIsNone(err)

        """ test consistent behavior between All, And """
        and_ = And(And(many[0], many[1]), many[2])
        (obj_, err_)= and_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_all_unknown_fuzzy_off(self):
        many = [self.price_btw_100_200, self.unknown_exception, self.price_btw_50_101, self.unknown_error]
        all_ = All(*many)
        (obj, err) = all_(self.stdCtx)
        self.assertEqual(obj, Criteria.ERROR)
        self.assertIsInstance(err, Exception)

        and_ = And(many[0], many[1])
        and_ = And(and_, many[2])
        and_ = And(and_, many[3])
        (obj_, err_) = and_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_all_unknown_fuzzy_on(self):
        many = [self.price_btw_100_200, self.unknown_error, self.price_btw_50_101]
        all_ = All(*many)
        (obj, err) = all_(self.fuzzyCtx)
        self.assertTrue(obj)
        self.assertIsInstance(err, KeyError)

        and_ = And(And(many[0], many[1]), many[2])
        (obj_, err_) = and_(self.fuzzyCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_all_error_fuzzy_off(self):
        many = [self.price_btw_100_200, self.error_error, self.price_btw_50_101]
        all_ = All(*many)
        (obj, err) = all_(self.stdCtx)
        self.assertEqual(obj, Criteria.ERROR)
        self.assertIsInstance(err, KeyError)

        # should be the same as And
        and_ = And(many[0], many[1])
        and_ = And(and_, many[2])
        (obj_, err_) = and_(self.stdCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_all_error_fuzzy_on_with_3_criteria(self):
        many = [self.price_btw_100_200, self.none_error, self.price_btw_50_101]
        all_ = All(*many)
        (obj, err) = all_(self.fuzzyCtx)
        self.assertTrue(obj)
        self.assertIsInstance(err, KeyError)

        # should be the same as And
        and_ = And(And(many[0], many[1]), many[2])
        (obj_, err_) = and_(self.fuzzyCtx)
        self.assertEqual(obj, obj_)
        self.assertEqual(err, err_)

    def test_all_error_fuzzy_on(self):
        many = [self.none_error]
        all_ = All(*many)
        (obj, err) = all_(self.fuzzyCtx)
        self.assertEqual(obj, Criteria.UNKNOWN)
        self.assertIsInstance(err, KeyError)

    def test_ser_all(self):
        many = [self.price_btw_100_200, self.price_btw_99_101, self.price_btw_50_101]
        all_ = All(*many)
        text = str(all_)
        all2_ = to_criteria(text)
        text2 = str(all2_)
        self.assertEqual(text, text2)


if __name__ == '__main__':
    unittest.main()
