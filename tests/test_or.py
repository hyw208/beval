import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Or

class TestOr( TestCase ):
    """
    merged view:
                | right.true | right.false | right.error  | right.unknown
    ----------------------------------------------------------------------
    left.true   | true       | true        | true         | true
    left.false  | true       | false       | F | E        | F | U
    left.error  | T | E      | F | E       | U | E        | U | E
    left.unknown| T | U      | F | U       | U | E        | U | U
    """

    def test_and_simple_boolean( self ):
        or_ = Or( True_, True_ )
        ans, err = or_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        or_ = Or( True_, False_ )
        ans, err = or_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        or_ = Or( False_, True_ )
        ans, err = or_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        or_ = Or( False_, False_ )
        ans, err = or_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

    def test_and_and_nesting( self ):

        john_duke = Ctx( { "first_name": "John", "last_name": "Duke", "address": "New York, NY", "age": 31, "hair": "curly", "fuzzy": True } )

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
        ans, err = or_( john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()

