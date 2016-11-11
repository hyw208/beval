import unittest

from criteria import Ctx
from tests.test_all import BaseCriteriaTest
from tests.test_helper import Person


class TestCtx(BaseCriteriaTest):

    def test_targets(self):
        for (target, fuzzy) in [(Person("John", "Duke", True), False), ({"first_name": "John", "last_name": "Duke"}, True)]:
            ctx = Ctx(target, fuzzy)
            self.assertEqual(ctx["first_name"], "John")
            self.assertEqual(ctx["last_name"], "Duke")
            self.assertEqual(ctx.fuzzy, fuzzy)

    def test_fuzzy(self):
        with self.assertRaises(KeyError):
            self.john_duke
            self.john_duke["credit"]

        self.assertTrue(self.john_duke.fuzzy)


if __name__ == '__main__':
    unittest.main()
