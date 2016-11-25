import unittest
from unittest import TestCase
from beval.criteria import Ctx, to_criteria, Or, Any, Eq, criteria_class, cTrue, cFalse
from test_helper import acura_small


class TestOr(TestCase):

    def test_and_simple_boolean(self):
        or_ = Or(cTrue, cTrue)
        (ans, err) = or_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = str(or_)
        or2_ = to_criteria(text)
        text2 = str(or2_)
        self.assertEqual(text, text2)

        any_ = Any(cTrue, cTrue)
        (ans_, err_) = any_(Ctx({}))
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        text = str(any_)
        """ since there are only 2 operands, it's considered Or during parsing"""
        or2_ = to_criteria(text)
        self.assertIsInstance(or2_, Or)
        """ therefore during ser, it's different from str of any """
        text2 = str(or2_)
        self.assertNotEqual(text, text2)

        or_ = Or(cTrue, cFalse)
        (ans, err) = or_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = str(or_)
        or2_ = to_criteria(text)
        text2 = str(or2_)
        self.assertEqual(text, text2)

        any_ = Any(cTrue, cFalse)
        (ans_, err_) = any_(Ctx({}))
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        text = str(any_)
        """ since there are only 2 operands, it's considered Or during parsing"""
        or2_ = to_criteria(text)
        self.assertIsInstance(or2_, Or)
        """ therefore during ser, it's different from str of any """
        text2 = str(or2_)
        self.assertNotEqual(text, text2)

        or_ = Or(cFalse, cTrue)
        (ans, err) = or_(Ctx({}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = str(or_)
        or2_ = to_criteria(text)
        text2 = str(or2_)
        self.assertEqual(text, text2)

        any_ = Any(cFalse, cTrue)
        (ans_, err_) = any_(Ctx({}))
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        text = str(any_)
        """ since there are only 2 operands, it's considered Or during parsing"""
        or2_ = to_criteria(text)
        self.assertIsInstance(or2_, Or)
        """ therefore during ser, it's different from str of any """
        text2 = str(or2_)
        self.assertNotEqual(text, text2)

        or_ = Or(cFalse, cFalse)
        (ans, err) = or_(Ctx({}))
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = str(or_)
        or2_ = to_criteria(text)
        text2 = str(or2_)
        self.assertEqual(text, text2)

        any_ = Any(cFalse, cFalse)
        (ans_, err_) = any_(Ctx({}))
        self.assertEqual(ans, ans_)
        self.assertEqual(err, err_)

        text = str(any_)
        """ since there are only 2 operands, it's considered Or during parsing"""
        or2_ = to_criteria(text)
        self.assertIsInstance(or2_, Or)
        """ therefore during ser, it's different from str of any """
        text2 = str(or2_)
        self.assertNotEqual(text, text2)

    def test_and_and_nesting(self):
        with acura_small as acura:
            ctx = Ctx(acura)

            expected = "(source == 'USA' or ((make == 'Mazda' or type == 'Midsize') or maxprice == 18.8))"
            or_ = Or(
                Eq("source", "USA"),
                Or(
                    Or(
                        Eq("make", "Mazda"),
                        Eq("type", "Midsize")
                    ),
                    Eq("maxprice", 18.8)
                )
            )
            (ans, err) = or_(ctx)
            text = str(or_)
            self.assertEqual(expected, text)
            self.assertTrue(ans)
            self.assertIsNone(err)

            or2_ = to_criteria(expected)
            self.assertIsInstance(or2_, Or)
            self.assertEqual(expected, str(or2_))

            expected = "source == 'USA' or make == 'Mazda' or type == 'Midsize' or maxprice == 18.8"
            any_ = Any(Eq("source", "USA"), Eq("make", "Mazda"), Eq("type", "Midsize"), Eq("maxprice", 18.8))
            text = str(any_)
            self.assertEqual(expected, text)
            (ans_, err_) = any_(ctx)
            self.assertTrue(ans)
            self.assertEqual(ans, ans_)
            self.assertEqual(err, err_)
            self.assertNotEqual(str(or_), str(any_))

            any2_ = to_criteria(expected)
            self.assertIsInstance(any2_, Any)
            self.assertEqual(expected, str(any2_))


if __name__ == '__main__':
    unittest.main()
