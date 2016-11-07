import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, And
from tests.test_helper import House


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

    def test_filter_over_many_objects( self ):
        """ example of how it can be used """

        """ Say there are many houses available in the market """
        available_houses = [ Ctx( House( price ) ) for price in xrange( 100000, 500000, 10000 ) ]

        """ But I can only afford between 150,000 to 450,000 and I don't want house price at 400000 for some reason """
        my_price_range_criteria = Criteria().Ge( "price", 150000 ).Le( "price", 450000 ).And().Eq( "price", 400000 ).Not().And().Build()

        """ Is the first house within my search range? """
        ans, err = my_price_range_criteria( available_houses[ 0 ] )
        self.assertEqual( 150000 <= available_houses[ 0 ][ "price" ] <= 45000, ans  )
        self.assertIsNone( err )

        """ To use built-in filter, I have to create a func that returns True or False since criteria eval returns ans and err tuple """
        def predicate( house ):
            ans, _ = my_price_range_criteria( house )
            return ans

        """ Get all houses within my criteria """
        affordable_houses = filter( predicate, available_houses )
        self.assertGreater( len( available_houses ), len( affordable_houses ) )
        self.assertNotIn( 400000, [ ctx.target.price for ctx in affordable_houses ] )

    def test_fuzzy_match( self ):
        """ another example where fuzzy is turned on """

        my_house_search_criteria = Criteria().Ge( "price", 150000 ).Le( "price", 450000 ).And().Eq( "address", "NYC" ).Not().And().Build()
        """ When fuzzy is turned on, even though the house is missing address """
        ctx = Ctx( { "fuzzy": True, "price": 200000 } )
        """ It should still match fuzzy search """
        ans, err = my_house_search_criteria( ctx )
        self.assertTrue( ans )
        self.assertIsInstance( err, KeyError )

        """ When fuzzy is turned on, if the address does not match the criteria """
        ctx = Ctx( { "fuzzy": True, "price": 200000, "address": "NYC" } )
        """ It should NOT match fuzzy search """
        ans, err = my_house_search_criteria( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )

        """ If fuzzy is turned off """
        ctx = Ctx( { "price": 200000 } )
        """ It's missing address and it will report error missing address """
        ans, err = my_house_search_criteria( ctx )
        self.assertIsNone( ans )
        self.assertIsInstance( err, KeyError )


if __name__ == '__main__':
    unittest.main()

