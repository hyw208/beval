import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne

class TestNe( TestCase ):

    def setUp( self ):
        """ create a dummy target """
        self.target = { "first_name": "John", "last_name": "Duke" }

    def test_ne_simple( self ):
        """ set up a criteria, checking if the first_name of the target is "John" """
        ne1 = Ne( "first_name", "John" ) # it means: first_name != "John"
        ne2 = Ne( "first_name", "John2" ) # it means: first_name != "John2"
        ne3 = Ne( "address", "New York, New York" ) # it means: address != "New York, New York"

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        ans, err = ne1( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        ans, err = ne2( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        ans, err = ne3( ctx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()