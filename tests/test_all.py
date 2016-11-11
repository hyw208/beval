import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Le, Lt, Btw, All, And, True_
from tests.test_helper import MockCriteria


class TestAll( TestCase ):


    def setUp( self ):
        self.target = { "price": 100 }

        self.stdCtx = Ctx( self.target )
        self.fuzzyCtx = Ctx( self.target, fuzzy = True )

        self.price_btw_100_200 = Btw( 100, "price", 200 )
        self.price_btw_99_101 = Btw( 99, "price", 101 )
        self.price_btw_50_101 = Btw( 50, "price", 101 )
        self.price_btw_98_99 = Btw( 98, "price", 99 )

        self.unknown_exception = MockCriteria( Criteria.UNKNOWN, Exception( "Address not found" ) )
        self.unknown_error = MockCriteria( Criteria.UNKNOWN, KeyError( "Address not found" ) )
        self.error_error = MockCriteria( Criteria.ERROR, KeyError( "Address not found" ) )
        self.none_error = MockCriteria( None, KeyError( "Address not found" ) )

    def test_all_positive( self ):
        many = [ self.price_btw_100_200, self.price_btw_99_101, self.price_btw_50_101 ]
        all_ = All( *many )

        ans, err = all_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        """ test consistent behavior between All, And """
        and_ = And( And( many[ 0 ], many[ 1 ] ), many[ 2 ] )

        ans_, err_ = and_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_negative( self ):
        many = [ self.price_btw_100_200, self.price_btw_98_99, self.price_btw_50_101 ]
        all_ = All( *many )

        ans, err = all_( self.stdCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        """ test consistent behavior between All, And """
        and_ = And( And( many[ 0 ], many[ 1 ] ), many[ 2 ] )

        ans_, err_ = and_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_unknown_fuzzy_off( self ):
        many = [ self.price_btw_100_200, self.unknown_exception, self.price_btw_50_101, self.unknown_error ]
        all_ = All( *many )

        ans, err = all_( self.stdCtx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( err, Exception )

        and_ = And( many[ 0 ], many[ 1 ] )
        and_ = And( and_, many[ 2 ] )
        and_ = And( and_, many[ 3 ] )

        ans_, err_ = and_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_unknown_fuzzy_on( self ):
        many = [ self.price_btw_100_200, self.unknown_error, self.price_btw_50_101 ]
        all_ = All( *many )

        ans, err = all_( self.fuzzyCtx )
        self.assertTrue( ans )
        self.assertIsInstance( err, KeyError )

        and_ = And( And( many[ 0 ], many[ 1 ] ), many[ 2 ] )
        ans_, err_ = and_( self.fuzzyCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_error_fuzzy_off( self ):
        many = [ self.price_btw_100_200, self.error_error, self.price_btw_50_101 ]
        all_ = All( *many )
        ans, err = all_( self.stdCtx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( err, KeyError )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        ans_, err_ = and_( self.stdCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_error_fuzzy_on_with_3_criteria( self ):
        many = [ self.price_btw_100_200, self.none_error, self.price_btw_50_101 ]
        all_ = All( *many )

        ans, err = all_( self.fuzzyCtx )
        self.assertTrue( ans )
        self.assertIsInstance( err, KeyError )

        # should be the same as And
        and_ = And( And( many[ 0 ], many[ 1 ] ), many[ 2 ] )
        ans_, err_ = and_( self.fuzzyCtx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_error_fuzzy_on( self ):
        many = [ MockCriteria( None, KeyError( "Address not found" ) )  ]
        all_ = All( *many )

        ans, err = all_( self.fuzzyCtx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()
