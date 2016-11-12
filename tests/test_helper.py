from criteria import Criteria, Eq


class MockCriteria(Criteria):

    def __init__(self, obj, err):
        self._obj = obj
        self._err = err

    def __call__(self, ctx):
        return self._obj, self._err


class Person(object):

    @property
    def fuzzy(self):
        return self._fuzzy

    def __init__(self, first_name, last_name, fuzzy):
        self.first_name = first_name
        self._last_name = last_name
        self._fuzzy = fuzzy

    def last_name(self):
        return self._last_name


class House(object):

    @property
    def price(self):
        return self._price

    @property
    def address(self):
        return self._address

    def __init__(self, price, address="not important"):
        self._price = price
        self._address = address


class ObjErrorWhenComp(object):

    def __init__(self, clazz):
        self._clazz = clazz

    def __cmp__(self, other):
        raise self._clazz()
