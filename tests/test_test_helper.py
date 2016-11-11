import operator
import unittest

from criteria import Criteria, Ctx, In
from tests.test_all import BaseCriteriaTest
from tests.test_helper import MockCriteria, ObjErrorWhenComp


class TestMockCriteria(BaseCriteriaTest):

    def test_mock_simple(self):
        mock = MockCriteria(True, None)
        (ans, err) = mock(self.stdEmptyCtx)
        self.assertTrue(ans)
        self.assertIsNone(err)

        mock = MockCriteria(False, KeyError())
        (ans, err) = mock(self.stdEmptyCtx)
        self.assertFalse(ans)
        self.assertIsInstance(err, KeyError)

    def test_error_comp(self):
        obj = ObjErrorWhenComp(KeyError)
        with self.assertRaises(KeyError):
            operator.eq(obj, "AAA")

        in_ = In("Rating", "AAA", "AA", "A")
        ctx = Ctx({"Rating": obj})
        (ans, err) = in_(ctx)
        self.assertEqual(ans, Criteria.ERROR)
        self.assertIsInstance(err, KeyError)

        in_ = In("Rating", "AAA", "AA", "A")
        ctx = Ctx({"Rating": obj}, fuzzy=True)
        (ans, err) = in_(ctx)
        self.assertEqual(ans, Criteria.UNKNOWN)
        self.assertIsInstance(err, KeyError)


if __name__ == '__main__':
    unittest.main()
