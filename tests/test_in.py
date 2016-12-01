import unittest
from unittest import TestCase

from beval.criteria import Const, Ctx, In, to_criteria, universal
from test_helper import acura_small


class TestIn(TestCase):

    def test_in_simple(self):
        with acura_small as acura:
            in_ = In("make", "Acura")
            (ans, err) = in_(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

            in_ = In("make", "Ford", "Chrysler", "Eagle", "Honda", "Acura", "Mazda")
            (ans, err) = in_(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

            in_ = In("make", "Ford", )
            (ans, err) = in_(Ctx(acura))
            self.assertFalse(ans)
            self.assertIsNone(err)

            in_ = In("make", "Ford", "Chrysler", "Eagle", "Honda")
            (ans, err) = in_(Ctx(acura, True))
            self.assertFalse(ans)
            self.assertIsNone(err)

    def test_ser_in(self):
        with acura_small as acura:
            expected = "make in ('Acura',)"
            in_ = to_criteria(expected)
            text = str(in_)
            self.assertEqual(expected, text)

            expected = "make in ('Ford','Chrysler','Eagle','Honda','Acura','Mazda',)"
            in_ = to_criteria(expected)
            text = str(in_)
            self.assertEqual(expected, text)
            (ans, err) = in_(Ctx(acura))
            self.assertTrue(ans)
            self.assertIsNone(err)

    def test_ser_simple_math(self):
        expected = "1 in (4,3,2,1,0,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, 1)
        self.assertEqual(in_.right, (4, 3, 2, 1, 0,))
        (ans, err) = in_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)

        expected = "1 in (4,3,2,0,-1,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, 1)
        self.assertEqual(in_.right, (4, 3, 2, 0, -1,))
        (ans, err) = in_(Ctx({}))
        self.assertFalse(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)

    def test_ser_simple_str(self):
        expected = "True in (False,'False',0,1,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, True)
        self.assertEqual(in_.right, (False, 'False', 0, 1,))
        (ans, err) = in_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)

    def test_universal(self):
        in_ = In("make", universal)
        expected = "make in ('*',)"
        self.assertEqual(expected, str(in_))

        in_ = to_criteria(expected)
        self.assertIn(universal, in_.right)
        self.assertEqual(expected, str(in_))

        for value in ("xyz", 1, 0, 10.3, False, True, object(), "*"):
            car = {"make": value}
            (ans, err) = in_(car)
            self.assertTrue(ans)
            self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
