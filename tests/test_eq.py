import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq
from tests.test_all import BaseCriteriaTest


class TestEq( BaseCriteriaTest ):


    def test_eq_positive( self ):
        eq = Eq( "first_name", "John" )
        ans, _ = eq( self.john_duke )
        self.assertTrue( ans )

    def test_eq_negative( self ):
        eq = Eq( "first_name", "Paul" )
        ans, err = eq( self.john_duke )
        self.assertFalse( ans )
        self.assertIsNone( err )

    def test_eq_unknown_fuzzy_true( self ):
        eq = Eq( "middle_name", "Joe" )
        ans, error = eq( self.john_duke )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( error, KeyError )

    def test_eq_unknown_fuzzy_false( self ):
        import copy
        eq = Eq( "middle_name", "Joe" )
        john_duke = copy.copy( self.john_duke )
        john_duke.fuzzy = False
        ans, error = eq( john_duke )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( error, KeyError )

    def test_ser( self ):
        eq = Eq( "name", "John" )
        text = str( eq )
        self.assertEqual( text, "name == 'John'" )

        eq = Eq( "price", 1002 )
        text = str( eq )
        self.assertEqual( text, "price == 1002" )

        eq = Eq( "pass", True )
        text = str( eq )
        self.assertEqual( text, "pass == True" )


if __name__ == '__main__':
    unittest.main()
