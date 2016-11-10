import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Le, Lt, Btw, All, And, True_
from tests.test_helper import MockCriteria


class TestAll( TestCase ):


    def test_all_positive( self ):
        ctx = Ctx( { "price": 100 } )

        many = []
        many.append( Btw( 100, "price", 200 ) )
        many.append( Btw( 99, "price", 101 ) )
        many.append( Btw( 50, "price", 101 ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        ans_, err_ = and_( ctx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_negative( self ):
        ctx = Ctx( { "price": 100 } )
        many = []
        many.append( Btw( 100, "price", 200 ) )
        many.append( Btw( 98, "price", 99 ) )
        many.append( Btw( 50, "price", 101 ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        ans_, err_ = and_( ctx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_unknown_fuzzy_off( self ):
        ctx = Ctx( { "price": 100 } )
        many = []
        many.append( Btw( 100, "price", 200 ) )
        many.append( MockCriteria( Criteria.UNKNOWN, Exception( "Address not found" ) ) )
        many.append( Btw( 50, "price", 101 ) )
        many.append( MockCriteria( Criteria.UNKNOWN, Exception( "Address not found" ) ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( err, Exception )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        and_ = And( and_, many[3] )
        ans_, err_ = and_( ctx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_unknown_fuzzy_on( self ):
        ctx = Ctx( { "price": 100 }, fuzzy = True )
        many = []
        many.append( Btw( 100, "price", 200 ) )
        many.append( MockCriteria( Criteria.UNKNOWN, KeyError( "Address not found" ) ) )
        many.append( Btw( 50, "price", 101 ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertTrue( ans )
        self.assertIsInstance( err, KeyError )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        ans_, err_ = and_( ctx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_error_fuzzy_off( self ):
        ctx = Ctx( { "price": 100 } )
        many = []
        many.append( Btw( 100, "price", 200 ) )
        many.append( MockCriteria( None, KeyError( "Address not found" ) ) )
        many.append( Btw( 50, "price", 101 ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( err, KeyError )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        ans_, err_ = and_( ctx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_error_fuzzy_on( self ):
        ctx = Ctx( { "price": 100 }, fuzzy = True )
        many = []
        many.append( Btw( 100, "price", 200 ) )
        many.append( MockCriteria( None, KeyError( "Address not found" ) ) )
        many.append( Btw( 50, "price", 101 ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        # should be the same as And
        and_ = And( many[0], many[1] )
        and_ = And( and_, many[2] )
        ans_, err_ = and_( ctx )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_all_error_fuzzy_on( self ):
        ctx = Ctx( { "price": 100 }, fuzzy = True )
        many = []
        many.append( MockCriteria( None, KeyError( "Address not found" ) ) )
        all_ = All( *many )
        ans, err = all_( ctx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()
