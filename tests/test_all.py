import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Between, All, And, to_criteria, Eq
from test_helper import acura_small as acura


class TestAll(TestCase):

    def test_all_positive(self):
        ctx = Ctx(acura)
        all_ = Criteria().Eq("make", "Acura").Between(15, "maxprice", 20.1).NotEq("source", "USA").Eq("type", "Small").All().Done()
        (ans, err) = all_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        and_ = Criteria().Eq("make", "Acura").Between(15, "maxprice", 20.1).And().NotEq("source", "USA").And().Eq("type", "Small").And().Done()
        (ans_, err_) = and_(ctx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

    def test_all_negative(self):
        ctx = Ctx(acura)
        all_ = Criteria().Eq("make", "Mazda").Between(15, "maxprice", 18).Eq("source", "USA").Eq("type","Midsize").All().Done()
        (ans, err) = all_(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        and_ = Criteria().Eq("make", "Mazda").Between(15, "maxprice", 18).And().Eq("source", "USA").And().Eq("type","Midsize").And().Done()
        (ans_, err_) = and_(ctx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

    def test_all_unknown_fuzzy_on_off(self):
        ctx = Ctx(acura, True)
        all_ = Criteria().Eq("x", "x").Eq("y", "y").Eq("z", "z").Eq("w", "w").All().Done()
        (ans, err) = all_(ctx)
        self.assertEqual(ans, Criteria.UNKNOWN)
        self.assertIsInstance(err, KeyError)

        and_ = Criteria().Eq("x", "x").Eq("y", "y").And().Eq("z", "z").And().Eq("w", "w").And().Done()
        (ans_, err_) = and_(ctx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err.message, err_.message)

        ctx = Ctx(acura, False)
        all_ = Criteria().Eq("x", "x").Eq("y", "y").Eq("z", "z").Eq("w", "w").All().Done()
        (ans, err) = all_(ctx)
        self.assertEqual(ans, Criteria.ERROR)
        self.assertIsInstance(err, KeyError)

        and_ = Criteria().Eq("x", "x").Eq("y", "y").And().Eq("z", "z").And().Eq("w", "w").And().Done()
        (ans_, err_) = and_(ctx)
        self.assertEqual(ans, ans_)
        self.assertEqual(err.message, err_.message)

    def test_ser_all(self):
        expected = "make == 'Acura' and 15 <= maxprice < 20.1 and source != 'USA' and type == 'Small'"
        all_ = Criteria().Eq("make", "Acura").Between(15, "maxprice", 20.1).NotEq("source", "USA").Eq("type","Small").All().Done()
        text = str(all_)
        self.assertEqual(expected, text)


if __name__ == '__main__':
    unittest.main()
