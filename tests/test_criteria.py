import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, And


class TestCriteria( TestCase ):


    def test_error_build( self ):
        with self.assertRaises( SyntaxError ):
            Criteria().Build()

    def test_criteria_simple( self ):
        c = Criteria()
        self.assertEqual( c.size(), 0 )

        c = Criteria().Eq( "Rating", "AA" ).Eq( "Country", "US" )
        self.assertEqual( c.size(), 2 )

        c = Criteria().Eq( "Rating", "AA" ).Eq( "Country", "US" ).And()
        self.assertEqual( c.size(), 1 )

        c = Criteria().Eq( "Rating", "AA" ).Eq( "Country", "US" ).And().Build()
        self.assertIsInstance( c, And )

        target = { "Rating": "AA", "Country": "US" }
        ctx = Ctx( target )
        ans, err = c( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

    def test_not( self ):
        c = Criteria().Eq( "Rating", "AA" ).Not().Build()
        target = { "Rating", "B" }
        ctx = Ctx( target )
        ans, err = c( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()


