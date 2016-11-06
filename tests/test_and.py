import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And

class TestAnd( TestCase ):
    """
            merged view:
                        right.true, right.false, right.error, right.none
            left.true   true        false        true|error   true|false
            left.false  (  return false, no need to check right  )
            left.error  true|error  false|error  none|error   none|error
            left.none   true|false  false|false  none|false   none|false
    """

    def test_and_simple_boolean( self ):
        and_ = And( True_, True_ )
        ans, err = and_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        and_ = And( True_, False_ )
        ans, err = and_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        and_ = And( False_, True_ )
        ans, err = and_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        and_ = And( False_, False_ )
        ans, err = and_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

    def test_and_and_nesting( self ):

        john_duke = Ctx( { "first_name": "John", "last_name": "Duke", "address": "New York, NY", "age": 31, "hair": "curly", "fuzzy": True } )

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
        ans, err = and_( john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()

