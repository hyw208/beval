
import operator

class Ctx( object ):
    """ Object that holds the target object evaluated by Criteria """

    @property
    def target( self ):
        """ real target object subject to comparison by criteria """
        return self._target

    @target.setter
    def target( self, target ):
        """ real target object subject to comparison by criteria """
        self._target = target

    def __init__( self, target ):
        """ real target object subject to comparison by criteria """
        self._target = target

    def __getitem__( self, item ):
        """ simple way of getting the info out of target object """

        if hasattr( self.target, "__getitem__" ):
            """ test dict like object """
            return self.target[ item ]

        elif hasattr( self.target, item ):
            """ it can work with either field, property or method """
            obj = getattr( self.target, item )
            return obj() if callable( obj ) else obj

        else:
            """ not sure how to get info out of target """
            raise KeyError( "Cannot get %s out of object of type %s" % ( item, type( self.target ) ) )

    def fuzzy( self ):
        """ determine if it should tolerate error accessing target object """
        try:
            ans = self[ "fuzzy" ]
            return ans

        except Exception:
            return False


def safe_monad( func ):
    """ monad style """
    try:
        obj = func()
        return ( obj, None )

    except Exception as err:
        return ( None, err )


def safe( func, fuzzy ):
    """ based on lenient flag, either return monad style or raise original error """
    ans, err = safe_monad( func )
    if err is None:
        return ( ans, None )

    elif fuzzy:
        return ( Criteria.UNKNOWN, err )

    else:
        raise err


class Criteria( object ):
    """ Criteria, eg Eq, NotEq, ... """
    UNKNOWN = "__UNKNOWN__"

    def __call__( self, ctx ):
        """ default to unknown """
        return Criteria.UNKNOWN

    def access( self, ctx, item ):
        """ get the item from ctx object """
        return safe( lambda: ctx[ item ], self.fuzzy( ctx ) )

    def fuzzy( self, ctx ):
        """ default to checking ctx's fuzzy policy """
        return ctx.fuzzy()


class Bool( Criteria ):
    """ not sure if we need it but for completeness """

    @property
    def one( self ):
        return self._one

    @one.setter
    def one( self, one ):
        self._one = one

    def __init__( self, one = False ):
        self._one = one

    def __call__( self, ctx ):
        return self.one

# true criteria
True_ = Bool( True )

# false criteria
False_ = Bool( False )


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
        """ check if ctx's info matches the condition inside eq criteria """
        obj, err = self.access( ctx, self.left )

        # obj can be anything, 1.3, None, "USA", Criteria.UNKNOWN etc
        if err is None:
            ans, _ = safe( lambda: self.op( obj, self.right ), self.fuzzy( ctx ) )
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
        """ always check left first,
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

        merged view:
                    right.true, right.false, right.error, right.none
        left.true   true        false        true|error   true|false
        left.false  (  return false, no need to check right  )
        left.error  true|error  false|error  none|error   none|error
        left.none   true|false  false|false  none|false   none|false
        """
        lans, lerr = self.left( ctx )
        if lans == False:
            # merged view:
            #             right.true, right.false, right.error, right.none
            # left.false  (  return false, no need to check right  )
            return False

        rans, rerr = self.right( ctx )
        if lans == True:
            # merged view:
            #             right.true, right.false, right.error, right.none
            # left.true   true        false        true|error   true|false
            if rans == True:
                # right.true
                return True

            elif rans == False:
                # right.false
                return False

            elif rans == Criteria.UNKNOWN:
                # right.none
                return True if self.fuzzy( ctx ) else False

            else:
                # right.error
                if self.fuzzy( ctx ):
                    return True
                else:
                    raise rerr

        elif lans == Criteria.UNKNOWN:
            # merged view:
            #             right.true, right.false, right.error, right.none
            # left.none   true|false  false|false  none|false   none|false
            if rans == True:
                # right.true
                return True if self.fuzzy( ctx ) else False

            elif rans == False:
                # right.false
                return False

            else:
                # right.error, right.none
                return Criteria.UNKNOWN if self.fuzzy( ctx ) else False

        else:
            # merged view:
            #             right.true, right.false, right.error, right.none
            # left.error  true|error  false|error  none|error   none|error
            if rans == True:
                # right.true
                if self.fuzzy( ctx ):
                    return True
                else:
                    raise rerr

            elif rans == False:
                # right.false
                if self.fuzzy( ctx ):
                    return False
                else:
                    raise rerr

            else:
                # right.error, right.none
                if self.fuzzy( ctx ):
                    return Criteria.UNKNOWN
                else:
                    raise rerr


class Or( Criteria ):
    pass


class Not( Criteria ):
    pass

