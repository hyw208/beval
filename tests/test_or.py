import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Or, Any
from tests.test_all import BaseCriteriaTest


class TestOr( BaseCriteriaTest ):


    def test_and_simple_boolean( self ):
        or_ = Or( True_, True_ )
        ans, err = or_( self.stdEmptyCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        any_ = Any( True_, True_ )
        ans_, err_ = any_( self.stdEmptyCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        or_ = Or( True_, False_ )
        ans, err = or_( self.stdEmptyCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        any_ = Any( True_, False_ )
        ans_, err_ = any_( self.stdEmptyCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        or_ = Or( False_, True_ )
        ans, err = or_( self.stdEmptyCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        any_ = Any( False_, True_ )
        ans_, err_ = any_( self.stdEmptyCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        or_ = Or( False_, False_ )
        ans, err = or_( self.stdEmptyCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        any_ = Any( False_, False_ )
        ans_, err_ = any_( self.stdEmptyCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_and_and_nesting( self ):
        or_ = Or(
            Eq( "last_name", "Duke" ),
            Eq( "first_name", "John" )
        )
        or_ = Or(
            or_,
            Eq( "age", 31 )
        )
        or_ = Or(
            Eq( "hair", "straight" ),
            or_
        )
        ans, err = or_( self.john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )

        any_ = Any( Eq( "hair", "straight" ), Eq( "last_name", "Duke" ), Eq( "first_name", "John" ), Eq( "age", 31 ) )
        ans_, err_ = any_( self.john_duke )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )


if __name__ == '__main__':
    unittest.main()

