import unittest
from unittest import TestCase
from beval.criteria import Const, Ctx, Eq, criteria_class
from test_helper import acura_small


class TestCtx(TestCase):

    def test_get(self):
        ctx = Ctx(acura_small)
        make = ctx["make"]
        self.assertEqual(make, "Acura")

        with self.assertRaises(KeyError):
            ctx["cpu"]

        cpu = ctx.get("cpu", default="Intel")
        self.assertEqual(cpu, "Intel")

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

    def test_criteria_class_override(self):
        eq = Eq("make", "Subaru")
        (ans, err) = eq({"make": "Subaru"})
        self.assertTrue(ans)
        self.assertIsNone(err)

        """ create a diff ctx class """
        class Ctx2(Ctx):
            def key(self, key):
                raise KeyError("no key %s" % key)

        """ back up the original ctx cls """
        cls = criteria_class.lookup(Const.Ctx)

        """ override ctx impl cls temporarily """
        criteria_class.override(Const.Ctx, Ctx2)

        eq = Eq("make", "Subaru")
        (ans, err) = eq({"make": "Subaru"})
        self.assertEqual(ans, Const.ERROR)
        self.assertIsInstance(err, KeyError)

        """ restore the original ctx impl cls """
        criteria_class.override(Const.Ctx, cls)


if __name__ == '__main__':
    unittest.main()
