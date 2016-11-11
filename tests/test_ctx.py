import unittest
from unittest import TestCase
from criteria import Ctx
from tests.test_helper import Person
from tests.test_all import BaseCriteriaTest


class TestCtx( BaseCriteriaTest ):


    def test_targets( self ):
        """ target can be a dict or any object """
        for target, fuzzy in [ ( Person( "John", "Duke", True ), False ), ( { "first_name": "John", "last_name": "Duke" }, True ) ]:
            ctx = Ctx( target, fuzzy )
            self.assertEqual( ctx[ "first_name" ], "John" )
            self.assertEqual( ctx[ "last_name" ], "Duke" )
            self.assertEqual( ctx.fuzzy, fuzzy )

    def test_fuzzy( self ):
        """ access info from target will sometimes result in error """
        with self.assertRaises( KeyError ):
            self.john_duke
            self.john_duke[ "credit" ]

        """ fuzzy however is safe guarded by ctx """
        self.assertTrue( self.john_duke.fuzzy )


if __name__ == '__main__':
    unittest.main()