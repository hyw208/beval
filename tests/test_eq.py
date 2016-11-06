import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq

class TestEq( TestCase ):

    def setUp( self ):
        """ create a dummy target """
        self.target = { "first_name": "John", "last_name": "Duke", "fuzzy": True }

    def test_eq_positive( self ):
        """ set up a criteria, checking if the first_name of the target is "John" """
        eq = Eq( "first_name", "John" )

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        ans, _ = eq( ctx )
        self.assertTrue( ans )

    def test_eq_negative( self ):
        """ set up a criteria, checking if the first_name of the target is "John" """
        eq = Eq( "first_name", "Paul" )

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        ans, err = eq( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )

    def test_eq_unknown_fuzzy_true( self ):
        """ """
        eq = Eq( "middle_name", "Joe" )

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        ans, error = eq( ctx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( error, KeyError )

    def test_eq_unknown_fuzzy_false( self ):
        """ """
        eq = Eq( "middle_name", "Joe" )

        """ wrap inside ctx """
        target = self.target.copy()
        target[ "fuzzy" ] = False
        ctx = Ctx( target )

        """ test """
        ans, error = eq( ctx )
        self.assertIsNone( ans )
        self.assertIsInstance( error, KeyError )


if __name__ == '__main__':
    unittest.main()
