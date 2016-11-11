import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Not, In
from tests.test_helper import MockCriteria, ObjErrorWhenComp
import operator

class TestMockCriteria( TestCase ):


    def test_mock_simple( self ):
        mock = MockCriteria( True, None )
        ans, err = mock( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        mock = MockCriteria( False, KeyError() )
        ans, err = mock( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsInstance( err, KeyError )

    def test_error_comp( self ):
        obj = ObjErrorWhenComp( KeyError )
        with self.assertRaises( KeyError ):
            operator.eq( obj, "AAA" )

        in_ = In( "Rating", "AAA", "AA", "A" )
        ctx = Ctx( { "Rating": obj } )
        ans, err = in_( ctx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( err, KeyError )

        in_ = In( "Rating", "AAA", "AA", "A" )
        ctx = Ctx( { "Rating": obj, "fuzzy": True } )
        ans, err = in_( ctx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()

