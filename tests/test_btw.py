import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Le, Lt, Btw
from tests.test_all import BaseCriteriaTest


class TestBtw( BaseCriteriaTest ):


    def test_btw_simple( self ):
        btw_ = Btw( 100, "price", 200 ) # 100 <= price < 200
        ans, err = btw_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        btw_ = Btw( 99, "price", 101 ) # 99 <= price < 101
        ans, err = btw_( self.stdCtx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        btw_ = Btw( 101, "price", 200 ) # 101 <= price < 200
        ans, err = btw_( self.stdCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        btw_ = Btw( 60, "price", 100 ) # 60 <= price < 100
        ans, err = btw_( self.stdCtx )
        self.assertFalse( ans )
        self.assertIsNone( err )

    def test_missing_info_fuzzy_off( self ):
        btw_ = Btw( 100, "price", 200 ) # 100 <= price < 200
        ans, err = btw_( self.stdEmptyCtx )
        self.assertEqual( ans, Criteria.ERROR )
        self.assertIsInstance( err, KeyError )

    def test_fuzzy_on( self ):
        btw_ = Btw( 100, "price", 200 ) # 100 <= price < 200
        ans, err = btw_( self.fuzzyEmptyCtx )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()
