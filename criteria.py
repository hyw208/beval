
import operator

class Ctx( object ):
    """ Object that holds the target object evaluated by Criteria """

    @property
    def target( self ):
        return self._target

    @target.setter
    def target( self, target ):
        self._target = target

    def __init__( self, target ):
        self._target = target

    def __getitem__( self, item ):
        """ simple way of getting the info out of target object """
        if hasattr( self.target, "__getitem__" ):
            return self.target[ item ]

        elif hasattr( self.target, item ):
            obj = getattr( self.target, item )
            return obj() if callable( obj ) else obj

        else:
            raise KeyError( "Cannot get %s out of object of type %s" % ( item, type( self.target ) ) )

    def fuzzy( self ):
        """ determine if it should tolerate error accessing target object """
        try:
            ans = self[ "fuzzy" ]

        except Exception:
            return False

        else:
            return ans


class Criteria( object ):
    """ Criteria, eg Eq, NotEq, ... """
    UNKNOWN = "__UNKNOWN__"

    def __call__( self, ctx ):
        return Criteria.UNKNOWN

    def access( self, ctx, item ):
        """ get the item from ctx object """
        try:
            obj = ctx[ item ]

        except Exception as ex:
            if self.fuzzy( ctx ):
                return Criteria.UNKNOWN, ex

            else:
                raise ex

        else:
            return obj, None

    def fuzzy( self, ctx ):
        """ default to checking ctx's fuzzy policy """
        return ctx.fuzzy()


class Eq( Criteria ):
    """ The equal criteria """

    @property
    def left( self ):
        return self._left

    @left.setter
    def left( self, left ):
        self._left = left

    @property
    def right( self ):
        return self._right

    @right.setter
    def right( self, right ):
        self._right = right

    @property
    def op( self ):
        return self._op

    @op.setter
    def op( self, op ):
        self._op = op

    def __init__( self, left, right, op = operator.eq ):
        self._left = left
        self._right = right
        self._op = op

    def __call__( self, ctx ):
        obj, err = self.access( ctx, self.left )
        """
        obj can be anything, 1.3, None, "USA", Criteria.UNKNOWN etc
        """
        if err is None:
            try:
                ans = self.op( obj, self.right )

            except Exception as ex:
                if self.fuzzy( ctx ):
                    return Criteria.UNKNOWN

                else:
                    raise ex

            else:
                return ans
        else:
            """ it signals that it doesn't know how to compare """
            return Criteria.UNKNOWN


class Ne( Eq ):

    def __init__( self, left, right ):
        super( Ne, self ).__init__( left, right, operator.ne )


class Lt( Eq ):

    def __init__( self, left, right ):
        super( Lt, self ).__init__( left, right, operator.lt )


class Le( Eq ):

    def __init__( self, left, right ):
        super( Le, self ).__init__( left, right, operator.le )


class Gt( Eq ):

    def __init__( self, left, right ):
        super( Gt, self ).__init__( left, right, operator.gt )


class Ge( Eq ):

    def __init__( self, left, right ):
        super( Ge, self ).__init__( left, right, operator.ge )


class In( Eq ):
    pass


class NotIn( In ):
    pass


class And( Eq ):


    def __init__( self, left, right ):
        super( And, self ).__init__( left, right, operator.and_ )

    def __call__( self, ctx ):
        pass
        """
        * always check left first,
        1. if fuzzy is true: try to be lenient
                    right.true, right.false, right.error, right.none
        left.true   true        false        true         true
        left.false  (  return false, no need to check right  )
        left.error  true        false        none         none
        left.none   true        false        none         none

        2. if fuzzy is false: try to be strict
                    right.true, right.false, right.error, right.none
        left.true   true        false        error        false
        left.false  (  return false, no need to check right  )
        left.error  (  raise error, no need to check right   )
        left.none   (  return false, no need to check right  )

        merged view
                    right.true, right.false, right.error, right.none
        left.true   true        false        true|error   true|false
        left.false  (  return false, no need to check right  )
        left.error  true|error  false|error  none|error   none|error
        left.none   true|false  false|false  none|false   none|false
        """
"""
        lans, lerr = self.left( ctx )
        if not lans:

        if lerr is None:
            if lans or lans is None:


            else:
                return False
        else:
            if self.fuzzy( ctx ):

                rans, rerr = self.right( ctx )

            else:
                raise lerr
"""



class Or( Criteria ):
    pass


class Not( Criteria ):
    pass

