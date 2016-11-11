import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, All
from tests.test_helper import MockCriteria
from tests.test_all import BaseCriteriaTest


class TestAnd( BaseCriteriaTest ):


    def test_and_simple_boolean( self ):
        and_ = And( True_, True_ )
        ans, err = and_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        all_ = All( True_, True_ )
        ans_, err_ = all_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        and_ = And( True_, False_ )
        ans, err = and_( self.stdCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        all_ = All( True_, False_ )
        ans_, err_ = all_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        and_ = And( False_, True_ )
        ans, err = and_( self.stdCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        all_ = All( False_, True_ )
        ans_, err_ = all_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        and_ = And( False_, False_ )
        ans, err = and_( self.stdCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        all_ = All( False_, False_ )
        ans_, err_ = all_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_and_and_nesting( self ):
        and_ = And(
            Eq( "last_name", "Duke" ),
            Eq( "first_name", "John" )
        )
        and_ = And(
            and_,
            Eq( "age", 31 )
        )
        and_ = And(
            Ne( "hair", "straight" ),
            and_
        )
        ans, err = and_( self.john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )

        all_ = All( Ne( "hair", "straight" ), Eq( "last_name", "Duke" ), Eq( "first_name", "John" ), Eq( "age", 31 ) )
        ans_, err_ = all_( self.john_duke )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_and_nesting_err( self ):
        and_ = And( self.true_key_error_lf, self.true_key_error_rf )
        and_ = And( and_, self.true_key_error_r2nd )
        ans, err = and_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "left first" )

        and_ = And( self.true_key_error_lf, self.true_key_error_rf )
        and_ = And( self.true_key_error_r2nd, and_ )
        ans, err = and_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "left 2nd" )

    def test_and_left_true( self ):
        # left.true, right.true
        and_ = And( self.true_key_error_lf, self.true_key_error_rf )
        ans, err = and_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "left first" )

        # left.true, right.error, fuzzy.true
        and_ = And( True_, self.true_key_error_rf )
        ans, err = and_( self.fuzzyCtx )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "right first" )

        # left.true, right.error, fuzzy.false
        and_ = And( True_, self.none_error_rf )
        ans, err = and_( self.stdCtx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "right first" )

        # left.true, right.unknown, fuzzy.true
        and_ = And( True_, self.unknown_none )
        ans, err = and_( self.fuzzyCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        # left.true, right.unknown, fuzzy.false
        and_ = And( True_, self.unknown_none )
        ans, err = and_( self.stdCtx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()

