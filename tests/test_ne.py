import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne

class TestNe( TestCase ):

    def setUp( self ):
        """ create a dummy target """
        self.target = { "first_name": "John", "last_name": "Duke", "fuzzy": True }

    def test_ne_simple( self ):
        """ set up a criteria, checking if the first_name of the target is "John" """
        ne1 = Ne( "first_name", "John" )
        ne2 = Ne( "first_name", "John2" )
        ne3 = Ne( "address", "New York, New York" )

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        self.assertFalse( ne1( ctx ) )
        self.assertTrue( ne2( ctx ) )
        self.assertEqual( ne3( ctx ), Criteria.UNKNOWN )


if __name__ == '__main__':
    unittest.main()