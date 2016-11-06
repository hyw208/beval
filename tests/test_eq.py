import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq

class TestEq( TestCase ):

    def setUp( self ):
        """ create a dummy target """
        self.target = { "first_name": "John", "last_name": "Duke", "fuzzy": True }

    def test_eq_simple( self ):
        """ set up a criteria, checking if the first_name of the target is "John" """
        eq = Eq( "first_name", "John" )

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        self.assertTrue( eq( ctx ) )

    def test_eq_none( self ):
        """ """
        eq = Eq( "middle_name", "Joe" )

        """ wrap inside ctx """
        ctx = Ctx( self.target )

        """ test """
        ans = eq( ctx )
        self.assertEqual( ans, Criteria.UNKNOWN )

    def test_eq_raise( self ):
        """ target has no middle name and fuzzy is set to False """
        eq = Eq( "middle_name", "Joe" )

        """ wrap inside ctx """
        target = self.target.copy()
        del target[ "fuzzy" ]

        """ force fuzzy test to be False """
        ctx = Ctx( target )

        """ test """
        with self.assertRaises( KeyError ):
            ans = eq( ctx )


if __name__ == '__main__':
    unittest.main()
