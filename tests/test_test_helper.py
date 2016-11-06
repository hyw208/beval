import unittest
from unittest import TestCase
from criteria import Criteria, Ctx, Eq, Ne, True_, False_, And, Not
from tests.test_helper import MockCriteria

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


if __name__ == '__main__':
    unittest.main()

