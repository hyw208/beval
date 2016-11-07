import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, And


class TestCriteria( TestCase ):


    def test_api( self ):
        c = Criteria()
        self.assertEqual( c.size(), 0 )

        c = Criteria().Eq( "Rating", "AA" ).Eq( "Country", "US" )
        self.assertEqual( c.size(), 2 )

        c = Criteria().Eq( "Rating", "AA" ).Eq( "Country", "US" ).And()
        self.assertEqual( c.size(), 1 )

        c = Criteria().Eq( "Rating", "AA" ).Eq( "Country", "US" ).And().build()
        self.assertIsInstance( c, And )

        target = { "Rating": "AA", "Country": "US" }
        ctx = Ctx( target )
        ans, err = c( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()


