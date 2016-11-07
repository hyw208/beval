from criteria import Eq


class MockCriteria( Eq ):


    def __init__( self, left, right ):
        super( MockCriteria, self ).__init__( left, right, None )

    def __call__( self, ctx ):
        return ( self.left, self.right )


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


class House( object ):

    def __init__( self, price, address = "not important" ):
        self._price = price
        self._address = address

    @property
    def price( self ):
        return self._price

    @property
    def address( self ):
        return self._address


class ObjErrorWhenComp( object ):


    def __init__( self, clazz ):
        self._clazz = clazz

    def __cmp__( self, other ):
        raise self._clazz()

