import operator
import unittest
from unittest import TestCase

from beval.criteria import Criteria, Const, NotEq, to_criteria, Ctx, In, universal
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
            self.assertEqual(ans, Const.ERROR)
            self.assertIsInstance(err, KeyError)

            c = NotEq("cpu", "Intel")
            (ans, err) = c(Ctx(acura, True))
            self.assertEqual(ans, Const.UNKNOWN)
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

    def test_universal(self):
        notEq = NotEq("make", universal)
        expected = "make != '*'"
        self.assertEqual(expected, str(notEq))

        notEq = to_criteria(expected)
        self.assertEqual(notEq.right, Const.universal)
        self.assertEqual(expected, str(notEq))

        for value in ("xyz", 1, 0, 10.3, False, True, object(), "*"):
            car = {"make": value}
            (ans, err) = notEq(car)
            self.assertFalse(ans)
            self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
