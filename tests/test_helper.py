from criteria import Eq


class MockCriteria( Eq ):


    def __init__( self, left, right ):
        super( MockCriteria, self ).__init__( left, right, None )

    def __call__( self, ctx ):
        return ( self.left, self.right )


class Person(object):


    def __init__(self, first_name, last_name, fuzzy):
        self.first_name = first_name
        self._last_name = last_name
        self._fuzzy = fuzzy

    def last_name(self):
        return self._last_name

    @property
    def fuzzy(self):
        return self._fuzzy