import operator
import unittest
from unittest import TestCase

from beval.criteria import Ctx
from test_helper import CompareError, acura_small


class TestHelper(TestCase):

    def test_compare_error(self):
        cmp_err = CompareError(Exception('test compare error'))
        with self.assertRaises(Exception):
            operator.gt(cmp_err, 99)

    def test_car_attributes(self):
        with acura_small as acura:
            self.assertEqual(acura.make, 'Acura')
            self.assertEqual(acura.type, 'Small')
            self.assertEqual(acura.maxprice, 18.8)
            with self.assertRaises(AttributeError):
                acura.not_such_attribute

        ctx = Ctx(acura, fuzzy=False)
        self.assertEqual(acura.make, ctx['make'])
        self.assertEqual(acura.type, ctx['type'])
        self.assertEqual(acura.maxprice, ctx['maxprice'], 18.8)
        with self.assertRaises(KeyError):
            ctx['not_such_attribute']

        ctx = Ctx(acura, fuzzy=True)
        self.assertEqual(acura.make, ctx['make'])
        self.assertEqual(acura.type, ctx['type'])
        self.assertEqual(acura.maxprice, ctx['maxprice'], 18.8)
        with self.assertRaises(KeyError):
            ctx['not_such_attribute']

    def test_car_attribute_override(self):
        with acura_small as acura:
            self.assertEqual(acura.make, 'Acura')
            # now override the value so that it raises error during access
            acura.set_access_error('make', AttributeError())
            with self.assertRaises(AttributeError):
                acura.make

        with acura_small as acura:
            make = acura.make
            self.assertTrue(operator.eq(make, 'Acura'))
            # now override the value so that it raises error druing compare
            acura.set_compare_error('make', CompareError(Exception()))
            make = acura.make
            with self.assertRaises(Exception):
                operator.eq(make, 'Acura')


if __name__ == '__main__':
    unittest.main()
