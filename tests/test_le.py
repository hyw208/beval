import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Le


class TestLe( TestCase ):


    def test_le_positive( self ):
        """ set up a criteria, checking if the first_name of the target is "John" """
        le_ = Le( "price", 99.99 )

        """ wrap target inside ctx """
        ctx = Ctx( { "price": 99.98 } )
        ans, err = le_( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        """ wrap target inside ctx """
        ctx = Ctx( { "price": 99.99 } )
        ans, err = le_( ctx )
        self.assertTrue( ans )
        self.assertIsNone( err )

        """ wrap target inside ctx """
        ctx = Ctx( { "price": 99.999 } )
        ans, err = le_( ctx )
        self.assertFalse( ans )
        self.assertIsNone( err )


if __name__ == '__main__':
    unittest.main()
