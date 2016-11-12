import unittest
import operator
from criteria import Criteria, Ctx, toCriteria, Eq, Bool, Between
from tests.test_all import BaseCriteriaTest


class TestVisit(BaseCriteriaTest):

    def test_single_word_bool_criteria_alone(self):
        target = {"honest": True, "tall": "True"}
        std_ctx = Ctx(target)

        tests = []
        tests.append(('True', True, bool, True, None))
        tests.append(('"True"', 'True', bool, True, None))
        tests.append(('honest', 'honest', bool, True, None))
        tests.append(('tall', 'tall', bool, True, None))
        tests.append(('False', False, bool, False, None))
        tests.append(('"False"', 'False', bool, False, None))
        tests.append(('famous', 'famous', type(Criteria.ERROR), Criteria.ERROR, KeyError))

        for text_, equal_, type_, ans_, err_ in tests:
            c = toCriteria(text_)
            self.assertIsInstance(c, Criteria)
            self.assertEqual(c.one, equal_)

            (ans, err) = c(std_ctx)
            self.assertIsInstance(ans, type_)
            self.assertEqual(ans, ans_)
            if err_:
                self.assertIsInstance(err, err_)
            else:
                self.assertIsNone(err)

    def test_true_eq_true(self):
        """
        criteria.left is always turned into real True bool during evaluation
        """
        text = "True == 'True'"
        c = toCriteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, True)
        self.assertEqual(c.right, "True")
        (ans, err) = c(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = "'True' == 'True'"
        c = toCriteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, "True")
        self.assertEqual(c.right, "True")
        (ans, err) = c(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = "True == True"
        c = toCriteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, True)
        self.assertEqual(c.right, True)
        (ans, err) = c(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "'True' == True"
        c = toCriteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, "True")
        self.assertEqual(c.right, True)
        (ans, err) = c(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_simple_bool_eq(self):
        ctx = Ctx({"sunny": True})
        text = "sunny == True"
        c = toCriteria(text)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.left, "sunny")
        self.assertEqual(c.right, True)
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "sunny"
        c = toCriteria(text)
        self.assertIsInstance(c, Bool)
        self.assertEqual(c.one, "sunny")
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_between(self):
        text = "50 <= price < 100"
        c = toCriteria(text)
        self.assertIsInstance(c, Between)
        self.assertEqual(c.lower, 50)
        self.assertEqual(c.lower_op, operator.le)
        self.assertEqual(c.one, "price")
        self.assertEqual(c.upper_op, operator.lt)
        self.assertEqual(c.upper, 100)

        text = "44.1 < score <= 66.2"
        c = toCriteria(text)
        self.assertIsInstance(c, Between)
        self.assertEqual(c.lower, 44.1)
        self.assertEqual(c.lower_op, operator.lt)
        self.assertEqual(c.one, "score")
        self.assertEqual(c.upper_op, operator.le)
        self.assertEqual(c.upper, 66.2)



if __name__ == '__main__':
    unittest.main()
