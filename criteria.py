
import operator

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
        return ( None, err )

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
            return KeyError( "Cannot get %s out of object of type %s" % ( item, type( self.target ) ) )

    def fuzzy( self ):
        """ determine if it should tolerate error accessing target object """
        ans, err = safe_monad( lambda: self[ "fuzzy" ] )
        return False if err is not None else ans


class Criteria( object ):
    """ Criteria, eg Eq, NotEq, ... """
    UNKNOWN = "__UNKNOWN__"

    def __call__( self, ctx ):
        """ default to unknown if fuzzy is True """
        if self.fuzzy( ctx ):
            return Criteria.UNKNOWN

        else:
            raise NotImplementedError

    def fuzzy( self, ctx ):
        """ default to checking ctx's fuzzy policy """
        return ctx.fuzzy()

    def __init__( self ):
        self._stack = []

    def size( self ):
        return len( self._stack )

    def _push( self, item ):
        self._stack.append( item )

    def _pop( self ):
        return self._stack.pop()

    def Eq( self, left, right ):
        c = Eq( left, right )
        self._push( c )
        return self

    def Ne( self, left, right ):
        c = Ne( left, right )
        self._push( c )
        return self

    def Le( self, left, right ):
        c = Le( left, right )
        self._push( c )
        return self

    def Lt( self, left, right ):
        c = Lt( left, right )
        self._push( c )
        return self

    def Ge( self, left, right ):
        c = Ge( left, right )
        self._push( c )
        return self

    def Gt( self, left, right ):
        c = Gt( left, right )
        self._push( c )
        return self

    def Btw( self, lower, one, upper ):
        c = Btw( lower, one, upper )
        self._push( c )
        return self

    def In( self, left, *right ):
        c = In( left, *right )
        self._push( c )
        return self

    def NotIn( self, left, *right ):
        c = NotIn( left, *right )
        self._push( c )
        return self

    def And( self ):
        r, l = self._pop(), self._pop()
        c = And( l, r )
        self._push( c )
        return self

    def Or( self ):
        r, l = self._pop(), self._pop()
        c = Or( l, r )
        self._push( c )
        return self

    def Not( self ):
        c = Not( self._pop() )
        self._push( c )
        return self

    def Build( self ):
        if self.size() != 1:
            raise SyntaxError( "There are more items on stack: %d" % self.size() )

        else:
            return self._stack.pop()


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
        return ( self.one, None )

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
        obj, err = safe_monad( lambda: ctx[ self.left ] )
        """
        tuple has 2 states:
        1. ( val, None ): success getting the underlying info/val
        2. ( None, err ): error accessing underlying info/val
        """
        if err is not None:
            """ missing info to compare """
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( None, err )

        else:
            """ has some info to compare """
            obj_, err_ = safe( lambda: self.op( obj, self.right ), self.fuzzy( ctx ) )
            """
            tuple has 3 states:
                1. ( val, None ):                   val can be True or False
                2. ( Criteria.UNKNOWN, error ):     got error and fuzzy is True
                3. ( None, err ):                   got error and fuzzy is False
            """
            return ( obj_, err_ )


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


class Btw( Criteria ):


    @property
    def lower( self ):
        return self._lower

    @property
    def lowerOp( self ):
        return self._lowerOp

    @property
    def one( self ):
        return self._one

    @property
    def upperOp( self ):
        return self._upperOp

    @property
    def upper( self ):
        return self._upper

    def __init__( self, lower, one, upper, lowerOp = operator.le, upperOp = operator.lt ):
        self._lower = lower
        self._lowerOp = lowerOp
        self._one = one
        self._upperOp = upperOp
        self._upper = upper

    def __call__( self, ctx ):
        obj, err = safe_monad( lambda: ctx[ self.one ] )
        """
        tuple has 2 states:
        1. ( val, None ): success getting the underlying info/val
        2. ( None, err ): error accessing underlying info/val
        """
        if err is not None:
            """ missing info to compare """
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( None, err )

        else:
            obj_, err_ = safe( lambda: self.lowerOp( self.lower, obj ), self.fuzzy( ctx ) )
            """
            tuple has 3 states:
                1. ( val, None ):                   val can be True or False
                2. ( Criteria.UNKNOWN, error ):     got error and fuzzy is True
                3. ( None, err ):                   got error and fuzzy is False
            """
            if obj_ == True:
                obj2_, err2_ = safe( lambda: self.upperOp( obj, self.upper ), self.fuzzy( ctx ) )
                return ( obj2_, err2_ )
            else:
                return ( obj_, err_ )


class In( Eq ):


    def __init__( self, left, *right ):
        super( In, self ).__init__( left, right )

    def __call__( self, ctx ):
        obj, err = safe_monad( lambda: ctx[ self.left ] )
        """
        tuple has 2 states:
        1. ( val, None ): success getting the underlying info/val
        2. ( None, err ): error accessing underlying info/val
        """
        if err is not None:
            """ missing info to compare """
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( None, err )

        else:
            anyError = None
            for one in self.right:
                """ has some info to compare """
                obj_, err_ = safe_monad( lambda: self.op( obj, one ) )
                """
                tuple has 2 states:
                    1. ( val, None ):                   val can be True or False
                    2. ( None, err ):                   got error during cmp
                """
                if obj_ == True:
                    return ( obj_, err_ )

                if anyError is None and ( obj_ is None and err_ is not None ):
                    anyError = err_

            # no positive hit
            if anyError is None:
                return ( False, None )

            else:
                return ( Criteria.UNKNOWN, anyError ) if self.fuzzy( ctx ) else ( None, anyError )


class NotIn( In ):


    def __init__( self, left, *right ):
        super( NotIn, self ).__init__( left, *right )

    def __call__( self, ctx ):
        ans, err = super( NotIn, self ).__call__( ctx )
        """
        True
        False
        Criteria.UNKNOWN
        None, Error
        """
        if ans in ( True, False ):
            return ( not ans, err )
        else:
            return ( ans, err )


class And( Eq ):


    def __init__( self, left, right ):
        super( And, self ).__init__( left, right, operator.and_ )

    def __call__( self, ctx ):
        """ always check left first,
        if fuzzy is true: try to be lenient and give true or false
                    | right.true | right.false | right.error  | right.unknown
        ----------------------------------------------------------------------
        left.true   | true       | false       | true         | true
        left.false  | false      | false       | false        | false (due to short cut)
        left.error  | true       | false       | unknown      | unknown
        left.unknown| true       | false       | unknown      | unknown

        if fuzzy is false: try to be strict and give what it is
                    | right.true | right.false | right.error  | right.unknown
        ----------------------------------------------------------------------
        left.true   | true       | false       | error        | unknown
        left.false  | false      | false       | false        | false (due to short cut)
        left.error  | error      | error       | error        | error (due to short cut)
        left.unknown| unknown    | unknown     | unknown      | unknown (due to short cut)

        merged view:
                    | right.true | right.false | right.error  | right.unknown
        ----------------------------------------------------------------------
        left.true   | true       | false       | T | E        | T | U
        left.false  | false      | false       | false        | false
        left.error  | T | E      | F | E       | U | E        | U | E
        left.unknown| T | U      | F | U       | U | U        | U | U
        """

        lans, lerr = self.left( ctx )
        """
        tuple has 4 states:
            1. ( val, None ):                   val can be True or False and there is no error
            2. ( val, error ):                  val can be True or False and there is error
            3. ( Criteria.UNKNOWN, error ):     got error but fuzzy is True
            4. ( None, error ):                 got error and fuzzy is False

        therefore lans has 4 states
            1. True
            2. False
            3. UNKNOWN: in error state but fuzzy is True
            4. None: in error state and fuzzy is False
        """

        if lans == False:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.false  | false      | false       | false        | false
            """
            return ( False, lerr )

        rans, rerr = self.right( ctx )
        if lans == True:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.true   | true       | false       | T | E        | T | U
            """
            if rans == True:
                # right.true
                return ( True, lerr or rerr )

            elif rans == False:
                # right.false
                return ( False, lerr or rerr )

            elif rans == Criteria.UNKNOWN:
                # right.unknown
                return ( True, lerr or rerr ) if self.fuzzy( ctx ) else ( Criteria.UNKNOWN, lerr or rerr )

            else:
                # right.error
                return ( True, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

        elif lans == Criteria.UNKNOWN:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.unknown| T | U      | F | U       | U | U        | U | U
            """
            if rans == True:
                # right.true
                return ( True, lerr or rerr ) if self.fuzzy( ctx ) else ( Criteria.UNKNOWN, lerr or rerr )

            elif rans == False:
                # right.false
                return ( False, lerr or rerr ) if self.fuzzy( ctx ) else ( Criteria.UNKNOWN, lerr or rerr )

            else:
                # right.error, right.unknown
                return ( Criteria.UNKNOWN, lerr or rerr )

        else:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.error  | T | E      | F | E       | U | E        | U | E
            """
            if rans == True:
                # right.true
                return ( True, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

            elif rans == False:
                # right.false
                return ( False, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

            else:
                # right.error, right.unknown
                return ( Criteria.UNKNOWN, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )


class Or( Eq ):


    def __init__( self, left, right ):
        super( Or, self ).__init__( left, right, operator.or_ )

    def __call__( self, ctx ):
        """ always check left first,
        if fuzzy is true: try to be lenient and give true or false
                    | right.true | right.false | right.error  | right.unknown
        ----------------------------------------------------------------------
        left.true   | true       | true        | true         | true (due to short cut)
        left.false  | true       | false       | false        | false
        left.error  | true       | false       | unknown      | unknown
        left.unknown| true       | false       | unknown      | unknown

        if fuzzy is false: try to be strict and give what it is
                    | right.true | right.false | right.error  | right.unknown
        ----------------------------------------------------------------------
        left.true   | true       | true        | true         | true (due to short cut)
        left.false  | true       | false       | error        | unknown
        left.error  | error      | error       | error        | error
        left.unknown| unknown    | unknown     | error        | unknown

        merged view:
                    | right.true | right.false | right.error  | right.unknown
        ----------------------------------------------------------------------
        left.true   | true       | true        | true         | true
        left.false  | true       | false       | F | E        | F | U
        left.error  | T | E      | F | E       | U | E        | U | E
        left.unknown| T | U      | F | U       | U | E        | U | U
        """

        lans, lerr = self.left( ctx )
        """
        tuple has 4 states:
            1. ( val, None ):                   val can be True or False and there is no error
            2. ( val, error ):                  val can be True or False and there is error
            3. ( Criteria.UNKNOWN, error ):     got error but fuzzy is True
            4. ( None, error ):                 got error and fuzzy is False

        therefore lans has 4 states
            1. True
            2. False
            3. UNKNOWN: in error state but fuzzy is True
            4. None: in error state and fuzzy is False
        """

        if lans == True:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
        (x) left.true   | true       | true        | true         | true
            left.false  | true       | false       | F | E        | F | U
            left.error  | T | E      | F | E       | U | E        | U | E
            left.unknown| T | U      | F | U       | U | E        | U | U
            """
            return ( True, lerr )

        rans, rerr = self.right( ctx )
        if lans == False:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.true   | true       | true        | true         | true
        (x) left.false  | true       | false       | F | E        | F | U
            left.error  | T | E      | F | E       | U | E        | U | E
            left.unknown| T | U      | F | U       | U | E        | U | U
            """
            if rans == True:
                # right.true
                return ( True, lerr or rerr )

            elif rans == False:
                # right.false
                return ( False, lerr or rerr )

            elif rans == Criteria.UNKNOWN:
                # right.unknown
                return ( False, lerr or rerr ) if self.fuzzy( ctx ) else ( Criteria.UNKNOWN, lerr or rerr )

            else:
                # right.error
                return ( False, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

        elif lans == Criteria.UNKNOWN:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.true   | true       | true        | true         | true
            left.false  | true       | false       | F | E        | F | U
            left.error  | T | E      | F | E       | U | E        | U | E
        (x) left.unknown| T | U      | F | U       | U | E        | U | U
            """
            if rans == True:
                # right.true
                return ( True, lerr or rerr ) if self.fuzzy( ctx ) else ( Criteria.UNKNOWN, lerr or rerr )

            elif rans == False:
                # right.false
                return ( False, lerr or rerr ) if self.fuzzy( ctx ) else ( Criteria.UNKNOWN, lerr or rerr )

            elif rans == Criteria.UNKNOWN:
                # right.unknown
                return ( Criteria.UNKNOWN, lerr or rerr )

            else:
                # right.error
                return ( Criteria.UNKNOWN, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

        else:
            """
            merged view:
                        | right.true | right.false | right.error  | right.unknown
            ----------------------------------------------------------------------
            left.true   | true       | true        | true         | true
            left.false  | true       | false       | F | E        | F | U
        (x) left.error  | T | E      | F | E       | U | E        | U | E
            left.unknown| T | U      | F | U       | U | E        | U | U
            """
            if rans == True:
                # right.true
                return ( True, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

            elif rans == False:
                # right.false
                return ( False, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )

            else:
                # right.error, right.unknown
                return ( Criteria.UNKNOWN, lerr or rerr ) if self.fuzzy( ctx ) else ( None, lerr or rerr )


class Not( Bool ):


    def __init__( self, one ):
        super( Not, self ).__init__( one )

    def __call__( self, ctx ):
        ans, err = self.one( ctx )
        """
        True
        False
        Criteria.UNKNOWN
        None
        """
        if ans in ( True, False ):
            return ( not ans, err )
        else:
            return ( ans, err )


