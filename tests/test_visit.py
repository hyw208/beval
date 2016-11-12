import unittest
import operator
from criteria import Criteria, Ctx, to_criteria, Eq, Bool, Between, Not, And, Or, Eq, NotEq, Gt, GtE, All, Any, In, NotIn
from tests.test_all import BaseCriteriaTest


class TestVisit(BaseCriteriaTest):

    def test_single_word_bool_criteria_alone(self):
        std_ctx = Ctx({"honest": True, "tall": "True"})

        tests = []
        tests.append(('True', True, bool, True, None))
        tests.append(('"True"', 'True', bool, True, None))
        tests.append(('honest', 'honest', bool, True, None))
        tests.append(('tall', 'tall', bool, True, None))
        tests.append(('False', False, bool, False, None))
        tests.append(('"False"', 'False', bool, False, None))
        tests.append(('famous', 'famous', type(Criteria.ERROR), Criteria.ERROR, KeyError))

        for text_, equal_, type_, ans_, err_ in tests:
            c = to_criteria(text_)
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
        c = to_criteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, True)
        self.assertEqual(c.right, "True")
        (ans, err) = c(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = "'True' == 'True'"
        c = to_criteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, "True")
        self.assertEqual(c.right, "True")
        (ans, err) = c(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = "True == True"
        c = to_criteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, True)
        self.assertEqual(c.right, True)
        (ans, err) = c(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "'True' == True"
        c = to_criteria(text)
        self.assertIsInstance(c, Criteria)
        self.assertEqual(c.left, "True")
        self.assertEqual(c.right, True)
        (ans, err) = c(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_simple_bool_eq(self):
        ctx = Ctx({"sunny": True})
        text = "sunny == True"
        c = to_criteria(text)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.left, "sunny")
        self.assertEqual(c.right, True)
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "sunny"
        c = to_criteria(text)
        self.assertIsInstance(c, Bool)
        self.assertEqual(c.one, "sunny")
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_between(self):
        text = "50 <= price < 100"
        c = to_criteria(text)
        self.assertIsInstance(c, Between)
        self.assertEqual(c.lower, 50)
        self.assertEqual(c.lower_op, operator.le)
        self.assertEqual(c.one, "price")
        self.assertEqual(c.upper_op, operator.lt)
        self.assertEqual(c.upper, 100)
        (ans, err) = c(Ctx({"price": 75}))
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "44.1 < score <= 66.2"
        c = to_criteria(text)
        self.assertIsInstance(c, Between)
        self.assertEqual(c.lower, 44.1)
        self.assertEqual(c.lower_op, operator.lt)
        self.assertEqual(c.one, "score")
        self.assertEqual(c.upper_op, operator.le)
        self.assertEqual(c.upper, 66.2)
        (ans, err) = c(Ctx({"score": 55.6}))
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_not(self):
        for text in ("not sunny", "not (sunny)"):
            not_sunny = to_criteria(text)
            self.assertIsInstance(not_sunny, Not)
            ctx = Ctx({"sunny": False})
            (ans, err) = not_sunny(ctx)
            self.assertTrue(ans)
            self.assertIsNone(err)

        for text in ("not 44.1 < score <= 66.2", "not (44.1 < score <= 66.2)",):
            c = to_criteria(text)
            self.assertIsInstance(c, Not)
            btw = c.one
            self.assertIsInstance(btw, Between)
            self.assertEqual(btw.lower, 44.1)
            self.assertEqual(btw.lower_op, operator.lt)
            self.assertEqual(btw.one, "score")
            self.assertEqual(btw.upper_op, operator.le)
            self.assertEqual(btw.upper, 66.2)

        for text in ("not sunny == True", "not (sunny == True)",):
            c = to_criteria(text)
            self.assertIsInstance(c, Not)
            eq = c.one
            self.assertEqual(eq.left, "sunny")
            self.assertEqual(eq.right, True)
            (ans, err) = eq(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)

    def test_bool_op_and(self):
        ctx = Ctx({"sunny": True, "score": 92})
        text = "sunny == True and score > 90"
        and_ = to_criteria(text)
        self.assertIsInstance(and_, And)
        eq_, gt_ = and_.left, and_.right
        self.assertIsInstance(eq_, Eq)
        self.assertIsInstance(gt_, Gt)
        (ans, err) = eq_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = gt_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = and_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_bool_op_all(self):
        ctx = Ctx({"sunny": True, "score": 92, "funny": False})
        text = "sunny and score >= 90 and funny != True"
        all_ = to_criteria(text)
        self.assertIsInstance(all_, All)
        sunny, score, funny = all_.many
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = all_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "sunny and (score >= 90 and funny != True)"
        and_ = to_criteria(text)
        self.assertIsInstance(and_, And)
        sunny = and_.left
        and_2nd = and_.right
        self.assertIsInstance(and_2nd, And)
        score, funny = and_2nd.left, and_2nd.right
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = and_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_bool_op_or(self):
        ctx = Ctx({"sunny": True, "score": 92})
        text = "sunny == True or score > 90"
        or_ = to_criteria(text)
        self.assertIsInstance(or_, Or)
        eq_, gt_ = or_.left, or_.right
        self.assertIsInstance(eq_, Eq)
        self.assertIsInstance(gt_, Gt)
        (ans, err) = eq_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = gt_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_bool_op_any(self):
        ctx = Ctx({"sunny": True, "score": 92, "funny": False})
        text = "sunny or score >= 90 or funny != True"
        any_ = to_criteria(text)
        self.assertIsInstance(any_, Any)
        sunny, score, funny = any_.many
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = any_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "sunny or (score >= 90 or funny != True)"
        or_ = to_criteria(text)
        self.assertIsInstance(or_, Or)
        sunny = or_.left
        or_2nd = or_.right
        self.assertIsInstance(or_2nd, Or)
        score, funny = or_2nd.left, or_2nd.right
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "(sunny or score >= 90) or funny != True"
        or_ = to_criteria(text)
        self.assertIsInstance(or_, Or)
        or_2nd = or_.left
        self.assertIsInstance(or_2nd, Or)
        sunny, score = or_2nd.left, or_2nd.right
        funny = or_.right
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_all_and_any_or(self):
        ctx = Ctx({"sunny": True, "score": 92, "funny": False})
        text = "sunny and score >= 90 or funny != True"
        or_ = to_criteria(text)
        self.assertIsInstance(or_, Or)
        and_ = or_.left
        funny = or_.right
        self.assertIsInstance(and_, And)
        sunny, score = and_.left, and_.right
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_in(self):
        ctx = Ctx({"sunny": True, "score": 92, "funny": False})
        text = "score in (90, 91, 92)"
        in_ = to_criteria(text)
        self.assertIsInstance(in_, In)
        self.assertEqual(len(in_.right), 3)
        (ans, err) = in_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

if __name__ == '__main__':
    unittest.main()
