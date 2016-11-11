import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Not
from tests.test_all import BaseCriteriaTest


class TestNot( BaseCriteriaTest ):


    def test_not_simple( self ):
        not_ = Not( True_ )
        ans, err = not_( self.stdEmptyCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        not_ = Not( False_ )
        ans, err = not_( self.stdEmptyCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

    def test_not_and( self ):
        and_ = And( True_, False_ )
        not_ = Not( and_ )
        ans, err = not_( self.stdEmptyCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

    def test_not_eq( self ):
        eq_ = Eq( "last_name", "Duke" )
        not_ = Not(
            eq_
        )
        ans, err = eq_( self.john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )

        ans, err = not_( self.john_duke )
        self.assertFalse( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()

