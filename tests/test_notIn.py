import unittest
from unittest import TestCase

from beval.criteria import Ctx, NotIn, to_criteria, universal
from test_helper import acura_small


class TestNotIn(TestCase):

    def test_in_simple(self):

        with acura_small as acura:
            ctx = Ctx(acura)
            not_in_ = NotIn("make", "Acura")
            (ans, err) = not_in_(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)

            not_in_ = NotIn("make", 'Ford','Chrysler','Eagle','Honda','Mazda', 'Acura')
            (ans, err) = not_in_(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)

            not_in_ = NotIn("make", 'Ford', 'Chrysler', 'Eagle', 'Honda', 'Mazda')
            (ans, err) = not_in_(ctx)
            self.assertTrue(ans)
            self.assertIsNone(err)

    def test_ser_not_in(self):

        with acura_small as acura:
            ctx = Ctx(acura)

            for expected in ("make not in ('Acura',)", "make not in ('Ford','Chrysler','Eagle','Honda','Acura',)"):
                not_in_ = to_criteria(expected)
                text = str(not_in_)
                self.assertEqual(expected, text)
                (ans, err) = not_in_(ctx)
                self.assertFalse(ans)
                self.assertIsNone(err)

            for expected in ("make not in ('Ford',)", "make not in ('Ford','Chrysler','Eagle','Honda','Mazda',)"):
                in_ = to_criteria(expected)
                text = str(in_)
                self.assertEqual(expected, text)
                (ans, err) = in_(ctx)
                self.assertTrue(ans)
                self.assertIsNone(err)

    def test_universal(self):
        notIn = NotIn("make", universal)
        expected = "make not in ('*',)"
        self.assertEqual(expected, str(notIn))

        notIn = to_criteria(expected)
        self.assertIn(universal, notIn.right)
        self.assertEqual(expected, str(notIn))

        for value in ("xyz", 1, 0, 10.3, False, True, object(), "*"):
            car = {"make": value}
            (ans, err) = notIn(car)
            self.assertFalse(ans)
            self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
