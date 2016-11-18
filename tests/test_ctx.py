import unittest
from unittest import TestCase
from criteria import Ctx
from test_helper import acura_small


class TestCtx(TestCase):

    def test_targets(self):
        with acura_small as acura:
            for fuzzy in (True, False):
                ctx = Ctx(acura, fuzzy)
                self.assertEqual(ctx["make"], "Acura")
                self.assertEqual(ctx["type"], "Small")
                self.assertEqual(ctx.fuzzy, fuzzy)

    def test_fuzzy(self):
        with acura_small as acura:
            for fuzzy in (True, False):
                ctx = Ctx(acura, fuzzy)
                with self.assertRaises(KeyError):
                    ctx["cpu"]


if __name__ == '__main__':
    unittest.main()
