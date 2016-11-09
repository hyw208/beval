import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Le, Lt, Btw


class TestBtw( TestCase ):


    def test_btw_simple( self ):
        ctx = Ctx( { "price": 100 } )

        btw_ = Btw( 100, "price", 200 ) # 100 <= price < 200
        ans, err = btw_( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        btw_ = Btw( 99, "price", 101 ) # 99 <= price < 101
        ans, err = btw_( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        btw_ = Btw( 101, "price", 200 ) # 101 <= price < 200
        ans, err = btw_( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        btw_ = Btw( 60, "price", 100 ) # 60 <= price < 100
        ans, err = btw_( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )

    def test_missing_info_fuzzy_off( self ):
        ctx = Ctx( { "address": "NYC" } )

        btw_ = Btw( 100, "price", 200 ) # 100 <= price < 200
        ans, err = btw_( ctx )
        self.assertIsNone( ans )
        self.assertIsInstance( err, KeyError )

    def test_fuzzy_on( self ):
        ctx = Ctx( { "address": "NYC", "fuzzy": True } )

        btw_ = Btw( 100, "price", 200 ) # 100 <= price < 200
        ans, err = btw_( ctx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()