import unittest
from criteria import Criteria, Ctx, Bool, cTrue, cFalse, Not
from tests.test_all import BaseCriteriaTest


class TestBool(BaseCriteriaTest):

    def test_basic_init(self):
        for ctx in [self.stdEmptyCtx, self.fuzzyEmptyCtx]:
            for c in [cTrue, Bool(True), Bool('True'), Bool(1)]:
                (obj, err) = c(ctx)
                self.assertTrue(obj)
                self.assertIsNone(err)

            for c in [cFalse, Bool(False), Bool('False'), Bool(0)]:
                (obj, err) = c(ctx)
                self.assertFalse(obj)
                self.assertIsNone(err)

    def test_supported_values(self):
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
        sunny = Bool("sunny")
        for value in values:
            ctx = Ctx({"sunny": value})
            (obj, err) = sunny(ctx)
            self.assertFalse(obj)
            self.assertIsNone(err)

            not_sunny = Not(sunny)
            (obj, err) = not_sunny(ctx)
            self.assertTrue(obj)
            self.assertIsNone(err)

    def test_unsupported_types_set_directly(self):
        """ set directly in __init__ """
        for ctx in [self.stdCtx, self.fuzzyCtx]:
            for value in [("test", "test"), {"test": "test"}, ]:
                with self.assertRaises(TypeError):
                    bool_ = Bool(value)

        """ set as value fetched from ctx """
        sunny = Bool('sunny')
        for fuzzy, err_ in [(False, Criteria.ERROR), (True, Criteria.UNKNOWN)]:
            for value in [("test", "test"), {"test": "test"}, ]:
                obj, err = sunny(Ctx({'sunny': value}, fuzzy))
                self.assertEqual(obj, err_)
                self.assertIsInstance(err, TypeError)

    def test_ser(self):
        bool_ = Bool(True)
        text = str(bool_)
        self.assertEqual(text, 'True')
        (ans, err) = bool_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        bool_ = Bool('True')
        text = str(bool_)
        self.assertEqual(text, 'True')
        (ans, err) = bool_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        bool_ = Bool(1)
        text = str(bool_)
        self.assertEqual(text, '1')
        (ans, err) = bool_(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        bool_ = Bool('funny')
        text = str(bool_)
        self.assertEqual(text, 'funny')
        (ans, err) = bool_(Ctx({"funny": True}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = bool_(Ctx({"funny": 'True'}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = bool_(Ctx({"funny": 1}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = bool_(Ctx({"funny": 0}))
        self.assertFalse(ans)
        self.assertIsNone(err)
        (ans, err) = bool_(Ctx({"funny": False}))
        self.assertFalse(ans)
        self.assertIsNone(err)
        (ans, err) = bool_(Ctx({"funny": 'False'}))
        self.assertFalse(ans)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
