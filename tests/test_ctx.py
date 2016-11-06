import unittest
from unittest import TestCase
from criteria import Ctx


class TestCtx( TestCase ):


    def test_targets( self ):
        """ target can be a dict or any object """
        class Person( object ):

            def __init__( self, first_name, last_name, fuzzy ):
                self.first_name = first_name
                self._last_name = last_name
                self._fuzzy = fuzzy

            def last_name( self ):
                return self._last_name

            @property
            def fuzzy( self ):
                return self._fuzzy

        for target in [ Person( "John", "Duke", True ), { "first_name": "John", "last_name": "Duke", "fuzzy": True } ]:
            ctx = Ctx( target )
            self.assertEqual( ctx[ "first_name" ], "John" )
            self.assertEqual( ctx[ "last_name" ], "Duke" )
            self.assertTrue( ctx[ "fuzzy" ] )

    def test_fuzzy( self ):
        """ access info from target will sometimes result in error """
        with self.assertRaises( KeyError ):
            ctx = Ctx( { "first_name": "John", "last_name": "Duke" } )
            ctx[ "fuzzy" ]

        """ fuzzy however is safe guarded by ctx """
        self.assertFalse( ctx.fuzzy() )


if __name__ == '__main__':
    unittest.main()