import unittest
from criteria import Criteria, Ctx, Bool, cTrue, cFalse
from tests.test_all import BaseCriteriaTest


class TestBool(BaseCriteriaTest):

    def test_basic_init(self):
        for ctx in [self.stdEmptyCtx, self.fuzzyEmptyCtx]:
            for c in [cTrue, Bool(True), Bool('True')]:
                (obj, err) = c(ctx)
                self.assertTrue(obj)
                self.assertIsNone(err)

            for c in [cFalse, Bool(False), Bool('False')]:
                (obj, err) = c(ctx)
                self.assertFalse(obj)
                self.assertIsNone(err)

    def test_supported_values(self):
        values = ['True', True, 'true', 'tRUE']
        active = Bool("active")
        for value in values:
            ctx = Ctx({"active": value})
            (obj, err) = active(ctx)
            self.assertTrue(obj)
            self.assertIsNone(err)

        values = [False, 'False', 'false', 'fALSE']
        sunny = Bool("sunny")
        for value in values:
            ctx = Ctx({"sunny": value})
            (obj, err) = sunny(ctx)
            self.assertFalse(obj)
            self.assertIsNone(err)

    def test_unsupported_types_set_directly(self):
        """ set directly in __init__ """
        for ctx in [self.stdCtx, self.fuzzyCtx]:
            for value in [0, 1, 0.99, {"test": "test"}, ]:
                with self.assertRaises(TypeError):
                    bool_ = Bool(value)

        """ set as value fetched from ctx """
        sunny = Bool('sunny')
        for fuzzy, err_ in [(False, Criteria.ERROR), (True, Criteria.UNKNOWN)]:
            for value in [0, 1, 0.99, {"test": "test"}, ]:
                obj, err = sunny(Ctx({'sunny': value}, fuzzy))
                self.assertEqual(obj, err_)
                self.assertIsInstance(err, TypeError)


if __name__ == '__main__':
    unittest.main()
