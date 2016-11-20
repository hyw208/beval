import unittest
from unittest import TestCase

from beval.criteria import Ctx, Bool, cTrue, cFalse, Not


class TestBool(TestCase):

    def test_basic_init(self):
        for ctx in [Ctx({}, False), Ctx({}, True)]:
            for c in [cTrue, Bool(True), Bool('True'), Bool(1)]:
                (obj, err) = c(ctx)
                self.assertTrue(obj)
                self.assertIsNone(err)

            for c in [cFalse, Bool(False), Bool('False'), Bool(0)]:
                (obj, err) = c(ctx)
                self.assertFalse(obj)
                self.assertIsNone(err)

    def test_basic_compare(self):
        values = ['True', True, 'true', 'tRUE', 1]
        active = Bool("active")
        for value in values:
            ctx = Ctx({"active": value})
            (obj, err) = active(ctx)
            self.assertTrue(obj)
            self.assertIsNone(err)

            not_active = Not(active)
            (obj, err) = not_active(ctx)
            self.assertFalse(obj)
            self.assertIsNone(err)

        values = [False, 'False', 'false', 'fALSE', 0]
        active = Bool("active")
        for value in values:
            ctx = Ctx({"active": value})
            (obj, err) = active(ctx)
            self.assertFalse(obj)
            self.assertIsNone(err)

            not_active = Not(active)
            (obj, err) = not_active(ctx)
            self.assertTrue(obj)
            self.assertIsNone(err)

    def test_unsupported_types(self):
        # direct injection into bool constructor
        for value in [(1,2,3), {"d": "d"}, ]:
            with self.assertRaises(TypeError):
                bool_ = Bool(value)

        # indirect injection as value looked up during comp
        for fuzzy in [True, False]:
            for value in [(1, 2, 3), {"d": "d"}, ]:
                active = Bool('active')
                (ans, err) = active(Ctx({"active": value}, fuzzy))
                self.assertIsInstance(err, TypeError)

    def test_ser(self):
        for value, expected in ((True, 'True'), ('True', 'True'), (1, '1'),):
            bool_ = Bool(value)
            self.assertEqual(str(bool_), expected)
            for ctx in (Ctx({}, False), Ctx({}, True),):
                (ans, err) = bool_(ctx)
                self.assertTrue(ans)
                self.assertIsNone(err)

        for value, expected in ((False, 'False'), ('False', 'False'), (0, '0'),):
            bool_ = Bool(value)
            self.assertEqual(str(bool_), expected)
            for ctx in (Ctx({}, False), Ctx({}, True),):
                (ans, err) = bool_(ctx)
                self.assertFalse(ans)
                self.assertIsNone(err)

        active = Bool('active')
        text = str(active)
        self.assertEqual(text, 'active')

        for value in (True, 'True', 1):
            (ans, err) = active(Ctx({"active": value}))
            self.assertTrue(ans)
            self.assertIsNone(err)

        for value in (False, 'False', 0):
            (ans, err) = active(Ctx({"active": value}))
            self.assertFalse(ans)
            self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
