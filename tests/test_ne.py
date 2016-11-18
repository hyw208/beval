import unittest
from unittest import TestCase
import operator
from criteria import Criteria, NotEq, to_criteria, Ctx
from test_helper import acura_small


class TestNe(TestCase):

    def test_ne_simple(self):

        with acura_small as acura:
            c = NotEq("make", "Acura")
            (ans, err) = c(Ctx(acura))
            self.assertFalse(ans)
            self.assertIsNone(err)

            c = NotEq("make", "Mazda")
            (ans, err) = c(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

            c = NotEq("cpu", "Intel")
            (ans, err) = c(Ctx(acura))
            self.assertEqual(ans, Criteria.ERROR)
            self.assertIsInstance(err, KeyError)

            c = NotEq("cpu", "Intel")
            (ans, err) = c(Ctx(acura, True))
            self.assertEqual(ans, Criteria.UNKNOWN)
            self.assertIsInstance(err, KeyError)

    def test_ser(self):

        with acura_small as acura:
            expected = "make != 'Acura'"
            not_eq = to_criteria(expected)
            text = str(not_eq)
            self.assertEqual(expected, text)
            self.assertIsInstance(not_eq, NotEq)
            self.assertEqual(not_eq.key, 'make')
            self.assertEqual(not_eq.right, 'Acura')
            self.assertEqual(not_eq.op, operator.ne)
            (ans, err) = not_eq(Ctx(acura))
            self.assertFalse(ans)
            self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
