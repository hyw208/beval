import unittest
from criteria import Criteria, Ctx, toCriteria
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


if __name__ == '__main__':
    unittest.main()
