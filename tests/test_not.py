import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Not

class TestNot( TestCase ):

    def test_not_simple( self ):
        not_ = Not( True_ )

        ans, err = not_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        not_ = Not( False_ )

        ans, err = not_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

    def test_not_and( self ):
        and_ = And( True_, False_ )
        not_ = Not( and_ )

        ans, err = not_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

    def test_not_eq( self ):
        john_duke = Ctx( { "first_name": "John", "last_name": "Duke", "address": "New York, NY", "age": 31, "hair": "curly", "fuzzy": True } )
        eq_ = Eq( "last_name", "Duke" )
        not_ = Not(
            eq_
        )

        ans, err = eq_( john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )

        ans, err = not_( john_duke )
        self.assertFalse( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()

