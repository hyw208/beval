import unittest
from unittest import TestCase

from beval.criteria import Criteria, Ctx, to_criteria, And
from test_helper import acura_midsize as acura, chevrolet_compact_e, chevrolet_compact_c, CARS


class TestCriteria(TestCase):

    def test_error_build(self):

        with self.assertRaises(SyntaxError):
            Criteria().Done()

    def test_criteria_simple(self):
        c = Criteria()
        self.assertEqual(c.size(), 0)

        c = Criteria().Eq("make", "Acura")
        self.assertEqual(c.size(), 1)

        c = Criteria().Eq("make", "Acura").Eq("type", "Midsize")
        self.assertEqual(c.size(), 2)

        c = Criteria().Eq("make", "Acura").Eq("type", "Midsize").And()
        self.assertEqual(c.size(), 1)

        c = Criteria().Eq("make", "Acura").Eq("type", "Midsize").And().Done()
        self.assertIsInstance(c, And)

        ctx = Ctx(acura)
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_not(self):
        c = Criteria().Eq("type", "Midsize").Not().Done()
        ctx = Ctx(acura)
        (ans, err) = c(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

    def test_fuzzy_match(self):
        car_search_criteria = Criteria().Between(17, "maxprice", 21).Eq("make", "Chevrolet").And().Eq("type", "Compact").And().Done()
        ctx = Ctx(chevrolet_compact_e)
        (ans, err) = car_search_criteria(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        ctx = Ctx(chevrolet_compact_c)
        (ans, err) = car_search_criteria(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        with chevrolet_compact_c as chevrolet_compact:
            """ make maxprice missing for chevrolet_compact temporarily """
            chevrolet_compact.set_access_error("maxprice", KeyError)
            ctx = Ctx(chevrolet_compact)
            (ans, err) = car_search_criteria(ctx)
            self.assertEqual(ans, Criteria.ERROR)
            self.assertIsInstance(err, KeyError)

            ctx = Ctx(chevrolet_compact, True)
            (ans, err) = car_search_criteria(ctx)
            self.assertTrue(ans)
            self.assertIsInstance(err, KeyError)

    def test_filter_cars(self):
        """ create criteria either through api or text """
        expected = "((17 <= maxprice < 21 and make == 'Chevrolet') and type == 'Compact')"
        car_search_criteria = Criteria().Between(17, "maxprice", 21).Eq("make", "Chevrolet").And().Eq("type", "Compact").And().Done()
        car_search_criteria2 = to_criteria(expected)
        self.assertEqual(str(car_search_criteria), expected)
        self.assertEqual(str(car_search_criteria2), expected)

        """ test that one of the cars below matches the criteria """
        ctx = Ctx(chevrolet_compact_e)
        (ans, err) = car_search_criteria(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        ctx = Ctx(chevrolet_compact_c)
        (ans, err) = car_search_criteria(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        """ to conform to built-in filter function's requirement """
        def predicate(car):
            (ans, _) = car_search_criteria(Ctx(car))
            return ans

        """ there should be only be one match """
        potential = filter(predicate, CARS)
        self.assertEqual(len(potential), 1)

        """ change search criteria a bit """
        car_search_criteria = Criteria().Eq("make", "Chevrolet").Eq("type", "Compact").Eq("source", "USA").All().Done()

        def predicate(car):
            (ans, _) = car_search_criteria(Ctx(car))
            return ans

        potential = filter(predicate, CARS)
        self.assertEqual(len(potential), 2)


if __name__ == '__main__':
    unittest.main()
