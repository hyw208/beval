import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Not, In, NotIn



class TestNotIn( TestCase ):


    def test_in_simple( self ):
        notIn_ = NotIn( "Rating", "BB" )
        ans, err = notIn_( Ctx( { "Rating": "BB" } ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        notIn_ = NotIn( "Rating", "AAA", "AA", "A", "BBB", "BB", "B" )
        ans, err = notIn_( Ctx( { "Rating": "BB" } ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        notIn_ = NotIn( "Rating", "AAA", "AA", "A" )
        ans, err = notIn_( Ctx( { "Rating": "BB" } ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

    def test_in_error( self ):
        pass


if __name__ == '__main__':
    unittest.main()

