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
    def setUp( self ):
        self.unknown = Eq( "Country", "USA" )
        self.target = { "first_name": "John", "last_name": "Duke", "fuzzy": True }

        self.error = Eq( "Rating", "USA" )
        self.target2 = { "first_name": "John", "last_name": "Duke", "fuzzy": False }


    def test_and_simple_boolean( self ):
        and_ = And( True_, True_ )
        self.assertTrue( and_( Ctx( {} ) ) )

        and_ = And( True_, False_ )
        self.assertFalse( and_( Ctx( {} ) ) )

        and_ = And( False_, True_ )
        self.assertFalse( and_( Ctx( {} ) ) )

        and_ = And( False_, False_ )
        self.assertFalse( and_( Ctx( {} ) ) )


if __name__ == '__main__':
    unittest.main()

