import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, All
from tests.test_helper import MockCriteria

class TestAnd( TestCase ):
    

    def test_and_simple_boolean( self ):
        and_ = And( True_, True_ )
        ans, err = and_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        all_ = All( True_, True_ )
        ans_, err_ = all_( Ctx( {} ) )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        and_ = And( True_, False_ )
        ans, err = and_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        all_ = All( True_, False_ )
        ans_, err_ = all_( Ctx( {} ) )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        and_ = And( False_, True_ )
        ans, err = and_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        all_ = All( False_, True_ )
        ans_, err_ = all_( Ctx( {} ) )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

        and_ = And( False_, False_ )
        ans, err = and_( Ctx( {} ) )
        self.assertFalse( ans )
        self.assertIsNone( err )

        all_ = All( False_, False_ )
        ans_, err_ = all_( Ctx( {} ) )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_and_and_nesting( self ):

        john_duke = Ctx( { "first_name": "John", "last_name": "Duke", "address": "New York, NY", "age": 31, "hair": "curly", "fuzzy": True } )

        and_ = And(
            Eq( "last_name", "Duke" ),
            Eq( "first_name", "John" )
        )

        and_ = And(
            and_,
            Eq( "age", 31 )
        )

        and_ = And(
            Ne( "hair", "straight" ),
            and_
        )
        ans, err = and_( john_duke )
        self.assertTrue( ans )
        self.assertIsNone( err )

        all_ = All( Ne( "hair", "straight" ), Eq( "last_name", "Duke" ), Eq( "first_name", "John" ), Eq( "age", 31 ) )
        ans_, err_ = all_( john_duke )
        self.assertEqual( ans, ans_ )
        self.assertEqual( err, err_ )

    def test_and_nesting_err( self ):
        and_ = And( MockCriteria( True, KeyError( "left first" ) ), MockCriteria( True, KeyError( "right first" ) ) )
        and_ = And( and_, MockCriteria( True, KeyError( "left 2nd" ) ) )
        ans, err = and_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "left first" )

        and_ = And( MockCriteria( True, KeyError( "left first" ) ), MockCriteria( True, KeyError( "right first" ) ) )
        and_ = And( MockCriteria( True, KeyError( "left 2nd" ) ), and_ )
        ans, err = and_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "left 2nd" )

    def test_and_left_true( self ):
        # left.true, right.true
        and_ = And( MockCriteria( True, KeyError( "left first" ) ), MockCriteria( True, KeyError( "right first" ) ) )
        ans, err = and_( Ctx( {} ) )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "left first" )

        # left.true, right.error, fuzzy.true
        and_ = And( True_, MockCriteria( None, KeyError( "right first" ) ) )
        ans, err = and_( Ctx( { "fuzzy": True } ) )
        self.assertTrue( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "right first" )

        # left.true, right.error, fuzzy.false
        and_ = And( True_, MockCriteria( None, KeyError( "right first" ) ) )
        ans, err = and_( Ctx( { "fuzzy": False } ) )
        self.assertIsNone( ans )
        self.assertIsNotNone( err )
        self.assertEqual( err.message, "right first" )

        # left.true, right.unknown, fuzzy.true
        and_ = And( True_, MockCriteria( Criteria.UNKNOWN, None ) )
        ans, err = and_( Ctx( { "fuzzy": True } ) )
        self.assertTrue( ans )
        self.assertIsNone( err )

        # left.true, right.unknown, fuzzy.false
        and_ = And( True_, MockCriteria( Criteria.UNKNOWN, None ) )
        ans, err = and_( Ctx( { "fuzzy": False } ) )
        self.assertEqual( ans, Criteria.UNKNOWN )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()

