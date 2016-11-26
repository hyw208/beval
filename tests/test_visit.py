import operator
import unittest
from unittest import TestCase
from beval.criteria import Criteria, Ctx, Const, to_criteria, Bool, Between, Not, And, Or, Eq, NotEq, Gt, GtE, All, Any, In, \
    NotIn, SyntaxAstCallExtender, criteria_class, safe_monad, _quote, operator_ser_symbol, bEvalVisitor


class TestVisit(TestCase):

    def test_single_word_bool_criteria_alone(self):
        ctx = Ctx({"active": True})

        tests = list()
        tests.append(('True', True, bool, True, None))
        tests.append(('"True"', 'True', bool, True, None))
        tests.append(('1', 1, bool, True, None))
        tests.append(('False', False, bool, False, None))
        tests.append(('"False"', 'False', bool, False, None))
        tests.append(('0', 0, bool, False, None))
        tests.append(('active', 'active', bool, True, None))
        tests.append(('cpu', 'cpu', type(Const.ERROR), Const.ERROR, KeyError))

        for (text_, equal_, type_, ans_, err_) in tests:
            c = to_criteria(text_)
            self.assertIsInstance(c, Criteria)
            self.assertIsInstance(c, Bool)
            self.assertEqual(c.key, equal_)

            (ans, err) = c(ctx)
            self.assertIsInstance(ans, type_)
            self.assertEqual(ans, ans_)
            self.assertIsInstance(err, err_) if err_ else self.assertIsNone(err)

    def test_true_eq_true(self):
        ctx = Ctx({})

        text = "True == 'True'"
        c = to_criteria(text)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.key, True)
        self.assertEqual(c.right, "True")
        (ans, err) = c(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = "'True' == 'True'"
        c = to_criteria(text)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.key, "True")
        self.assertEqual(c.right, "True")
        (ans, err) = c(ctx)
        self.assertFalse(ans)
        self.assertIsNone(err)

        text = "True == True"
        c = to_criteria(text)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.key, True)
        self.assertEqual(c.right, True)
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        text = "'True' == True"
        c = to_criteria(text)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.key, "True")
        self.assertEqual(c.right, True)
        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)

    def test_simple_bool_eq(self):
        ctx = Ctx({"active": True})

        expected = "active == True"
        c = to_criteria(expected)
        self.assertIsInstance(c, Eq)
        self.assertEqual(c.key, "active")
        self.assertEqual(c.right, True)

        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(c)
        self.assertEqual(expected, text)

        expected = "active"
        c = to_criteria(expected)
        self.assertIsInstance(c, Bool)
        self.assertEqual(c.key, "active")

        (ans, err) = c(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(c)
        self.assertEqual(expected, text)

    def test_between(self):
        expected = "50 <= price < 100"
        c = to_criteria(expected)
        self.assertIsInstance(c, Between)
        self.assertEqual(c.lower, 50)
        self.assertEqual(c.lower_op, operator.le)
        self.assertEqual(c.key, "price")
        self.assertEqual(c.upper_op, operator.lt)
        self.assertEqual(c.upper, 100)
        (ans, err) = c(Ctx({"price": 75}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(c)
        self.assertEqual(expected, text)

        expected = "44.1 < score <= 66.2"
        c = to_criteria(expected)
        self.assertIsInstance(c, Between)
        self.assertEqual(c.lower, 44.1)
        self.assertEqual(c.lower_op, operator.lt)
        self.assertEqual(c.key, "score")
        self.assertEqual(c.upper_op, operator.le)
        self.assertEqual(c.upper, 66.2)
        (ans, err) = c(Ctx({"score": 55.6}))
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(c)
        self.assertEqual(expected, text)

    def test_not(self):
        ctx = Ctx({"active": False, "score": 50})

        for text in ("not active", "not (active)"):
            not_active = to_criteria(text)
            self.assertIsInstance(not_active, Not)
            self.assertIsInstance(not_active.one, Bool)
            (ans, err) = not_active(ctx)
            self.assertTrue(ans)
            self.assertIsNone(err)
            ser = str(not_active)
            self.assertEqual("not (active)", ser)

        for text in ("not 44.1 < score <= 66.2", "not (44.1 < score <= 66.2)",):
            c = to_criteria(text)
            self.assertIsInstance(c, Not)
            btw = c.one
            self.assertIsInstance(btw, Between)
            self.assertEqual(btw.lower, 44.1)
            self.assertEqual(btw.lower_op, operator.lt)
            self.assertEqual(btw.key, "score")
            self.assertEqual(btw.upper_op, operator.le)
            self.assertEqual(btw.upper, 66.2)
            (ans, err) = c(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)
            ser = str(c)
            self.assertEqual("not (44.1 < score <= 66.2)", ser)

        for text in ("not active == True", "not (active == True)",):
            c = to_criteria(text)
            self.assertIsInstance(c, Not)
            eq = c.one
            self.assertEqual(eq.key, "active")
            self.assertEqual(eq.right, True)
            (ans, err) = eq(ctx)
            self.assertFalse(ans)
            self.assertIsNone(err)
            ser = str(c)
            self.assertEqual("not (active == True)", ser)

    def test_bool_op_and(self):
        ctx = Ctx({"active": 'True', "score": 92})
        text = "active == True and score > 90"
        and_ = to_criteria(text)
        self.assertIsInstance(and_, And)
        eq_, gt_ = and_.left, and_.right
        self.assertIsInstance(eq_, Eq)
        self.assertIsInstance(gt_, Gt)
        (ans, err) = eq_(ctx)
        self.assertFalse(ans)  # eq( True, 'True') is False
        self.assertIsNone(err)
        (ans, err) = gt_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        (ans, err) = and_(ctx)
        self.assertFalse(ans)  # False and True is False
        self.assertIsNone(err)

    def test_bool_op_all(self):
        ctx = Ctx({"active": True, "score": 92, "valid": False})

        original = "active and score >= 90 and valid != True"
        expected = original
        all_ = to_criteria(original)
        self.assertIsInstance(all_, All)
        active, score, valid = all_.many
        self.assertIsInstance(active, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(valid, NotEq)

        (ans, err) = all_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(all_)
        self.assertEqual(expected, text)

        original = "active and (score >= 90 and valid != True)"
        expected = "(active and (score >= 90 and valid != True))"
        and_ = to_criteria(original)
        self.assertIsInstance(and_, And)
        active = and_.left
        and_2nd = and_.right
        self.assertIsInstance(and_2nd, And)
        score, valid = and_2nd.left, and_2nd.right
        self.assertIsInstance(active, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(valid, NotEq)

        (ans, err) = and_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(and_)
        self.assertEqual(expected, text)

    def test_bool_op_or(self):
        ctx = Ctx({"active": True, "score": 92})
        original = "active == True or score > 90"
        expected = "(active == True or score > 90)"
        or_ = to_criteria(original)
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
        text = str(or_)
        self.assertEqual(expected, text)

    def test_bool_op_any(self):
        ctx = Ctx({"active": True, "score": 92, "valid": False})
        expected = "active or score >= 90 or valid != True"
        any_ = to_criteria(expected)
        self.assertIsInstance(any_, Any)
        sunny, score, funny = any_.many
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(funny, NotEq)
        (ans, err) = any_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(any_)
        self.assertEqual(expected, text)

        original = "active or (score >= 90 or valid != True)"
        expected = "(active or (score >= 90 or valid != True))"
        or_ = to_criteria(original)
        self.assertIsInstance(or_, Or)
        active = or_.left
        or_2nd = or_.right
        self.assertIsInstance(or_2nd, Or)
        score, valid = or_2nd.left, or_2nd.right
        self.assertIsInstance(sunny, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(valid, NotEq)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(or_)
        self.assertEqual(expected, text)

        original = "(active or score >= 90) or valid != True"
        expected = "((active or score >= 90) or valid != True)"
        or_ = to_criteria(original)
        self.assertIsInstance(or_, Or)
        or_2nd = or_.left
        self.assertIsInstance(or_2nd, Or)
        active, score = or_2nd.left, or_2nd.right
        valid = or_.right
        self.assertIsInstance(active, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(valid, NotEq)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(or_)
        self.assertEqual(expected, text)

    def test_all_and_any_or(self):
        ctx = Ctx({"active": 1, "score": 92, "valid": 0})
        original = "active and score >= 90 or valid != True"
        expected = "((active and score >= 90) or valid != True)"
        or_ = to_criteria(original)
        self.assertIsInstance(or_, Or)
        and_ = or_.left
        valid = or_.right
        self.assertIsInstance(and_, And)
        active, score = and_.left, and_.right
        self.assertIsInstance(active, Bool)
        self.assertIsInstance(score, GtE)
        self.assertIsInstance(valid, NotEq)
        (ans, err) = or_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(or_)
        self.assertEqual(expected, text)

    def test_in(self):
        ctx = Ctx({"score": 92})
        expected = "score in (90,91,92,)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, "score")
        self.assertEqual(len(in_.right), 3)
        (ans, err) = in_(ctx)
        self.assertTrue(ans)
        self.assertIsNone(err)
        text = str(in_)
        self.assertEqual(expected, text)

    def test_syntax_extender_with_group(self):

        class Group(object):

            CATEGORY = "category"
            NAMESPACE = "namespace"

            DEFAULT = "default"
            OFFICIAL = "official"

            @property
            def members(self):
                return self._members

            @property
            def category(self):
                return self._meta[Group.CATEGORY]

            @property
            def namespace(self):
                return self._meta[Group.NAMESPACE]

            def __init__(self, *members, **meta):
                self._members = members
                self._meta = meta
                self._meta[Group.CATEGORY] = meta[Group.CATEGORY] if Group.CATEGORY in meta else Group.DEFAULT
                self._meta[Group.NAMESPACE] = meta[Group.NAMESPACE] if Group.NAMESPACE in meta else Group.OFFICIAL

            def __str__(self):
                args = ",".join(_quote(member) for member in self._members)
                kwargs = ",".join("%s=%s" % (k, _quote(v)) for k, v in self._meta.iteritems())
                return "group(%s,%s)" % (args, kwargs)

            def values(self, ctx, key):
                """ just temp work to show the intention, values and groups should come from providers """
                many = list()
                for member in self._members:
                    if member == "domestic":
                        many.append("USA")
                    else:
                        many.append("nonUSA")

                return many

        class GroupAstCallExtender(SyntaxAstCallExtender):

            def name(self):
                return "group"

            def type(self):
                return Group

            def deserialize(self, *args, **kwargs):
                return Group(*args, **kwargs)

            def compare(self, ctx, key, op, left, group):
                for value in group.values(ctx, key):
                    if op(left, value):
                        return True
                return False

        SyntaxAstCallExtender.register(GroupAstCallExtender())

        expected = "source in (group('foreign',category='default',namespace='official'),)"
        in_ = to_criteria(expected)
        self.assertIsInstance(in_, In)
        self.assertEqual(in_.key, "source")
        self.assertIsInstance(in_.right[0], Group)

        (ans, err) = in_({"source": "nonUSA"})
        self.assertTrue(ans)
        self.assertIsNone(err)
        self.assertEqual(expected, str(in_))

        (ans, err) = in_({"source": "USA"})
        self.assertFalse(ans)
        self.assertIsNone(err)
        self.assertEqual(expected, str(in_))

        expected = "source not in (group('foreign',category='default',namespace='official'),)"
        not_in_ = to_criteria(expected)
        self.assertIsInstance(not_in_, NotIn)
        self.assertEqual(not_in_.key, "source")
        self.assertIsInstance(not_in_.right[0], Group)

        (ans, err) = not_in_({"source": "nonUSA"})
        self.assertFalse(ans)
        self.assertIsNone(err)
        self.assertEqual(expected, str(not_in_))

        (ans, err) = not_in_({"source": "USA"})
        self.assertTrue(ans)
        self.assertIsNone(err)
        self.assertEqual(expected, str(not_in_))

        expected = "group('foreign',category='default',namespace='official')"
        for group in (Group("foreign",category="default",namespace="official"), Group("foreign"),):
            self.assertEqual(group.members, ("foreign",))
            self.assertEqual(group.category, "default")
            self.assertEqual(group.namespace, "official")
            self.assertEqual(expected, str(group))


if __name__ == '__main__':
    unittest.main()
