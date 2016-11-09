import operator


def safe_monad( func, *args, **kwargs ):
    try:
        obj = func( *args, **kwargs )
        return ( obj, None )

    except Exception as err:
        return ( None, err )


def safe( fuzzy, func, *args, **kwargs ):
    ans, err = safe_monad( func, *args, **kwargs )
    if err is None:
        return ( ans, None )

    else:
        return ( Criteria.UNKNOWN, err ) if fuzzy else ( None, err )


def access( ctx, item ):
    return ctx[ item ]


class Criteria( object ):

    UNKNOWN = "__UNKNOWN__"

    def __call__( self, ctx ):
        raise NotImplementedError

    def fuzzy( self, ctx ):
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

    def All( self ):
        c = All( *self._stack )
        self._stack = [ c ]
        return self

    def Any( self ):
        c = Any( *self._stack )
        self._stack = [ c ]
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

    def __init__( self, target, fuzzy = None ):
        """ real target object subject to comparison by criteria """
        self._target = target
        self._fuzzy = fuzzy

    def __getitem__( self, item ):
        """ simple way of getting the info out of target object """

        if hasattr( self.target, "__getitem__" ) and item in self.target:
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
        """ return either True or False """
        if self._fuzzy is None:
            ans, err = safe_monad( access, self, "fuzzy" )
            return ans if err is None else False
        else:
            """ if set, either True or False, use it from ctx """
            return self._fuzzy


class Bool( Criteria ):


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
        obj, err = safe_monad( access, ctx, self.left )
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
            obj_, err_ = safe( self.fuzzy( ctx ), self.op, obj, self.right )

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
        obj, err = safe_monad( access, ctx, self.one )
        """
        tuple has 2 states:
        1. ( val, None ): success getting the underlying info/val
        2. ( None, err ): error accessing underlying info/val
        """
        if err is not None:
            """ missing info to compare """
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( None, err )

        else:
            obj_, err_ = safe( self.fuzzy( ctx ), self.lowerOp, self.lower, obj )
            """
            tuple has 3 states:
                1. ( val, None ):                   val can be True or False
                2. ( Criteria.UNKNOWN, error ):     got error and fuzzy is True
                3. ( None, err ):                   got error and fuzzy is False
            """
            if obj_ == True:
                obj2_, err2_ = safe( self.fuzzy( ctx ), self.upperOp, obj, self.upper )
                return ( obj2_, err2_ )
            else:
                return ( obj_, err_ )


class In( Eq ):


    def __init__( self, left, *right ):
        super( In, self ).__init__( left, right )

    def __call__( self, ctx ):
        obj, err = safe_monad( access, ctx, self.left )
        """
        tuple has 2 states:
        1. ( val, None ): success getting the underlying info/val, though val can be None
        2. ( None, err ): error accessing underlying info/val
        """
        if err is not None:
            """ missing info to compare """
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( None, err )

        else:
            firstError = None
            for one in self.right:
                obj_, err_ = safe_monad( self.op, obj, one )

                if obj_ == True:
                    return ( obj_, firstError or err_ )

                else:
                    # obj_ is either False or None
                    firstError = firstError or err_

            """ no positive hit """
            if firstError is None:
                return ( False, None )

            else:
                return ( Criteria.UNKNOWN, firstError ) if self.fuzzy( ctx ) else ( None, firstError )


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


class All( Criteria ):


    @property
    def many( self ):
        return self._many

    @many.setter
    def many( self, many ):
        self._many = many

    def __init__( self, *many ):
        self._many = many

    def __call__( self, ctx ):
        positives = 0
        firstError = None
        for one in self.many:
            ans, err = one( ctx )
            """
            1. True
            2. False
            3. UNKNOWN: in error state but fuzzy is True
            4. None: in error state and fuzzy is False
            """
            if ans == True:
                positives += 1
                firstError = firstError or err

            elif ans == False:
                return ( ans, firstError or err )

            else:
                if self.fuzzy( ctx ):
                    firstError = firstError or err

                else:
                    return ( ans, firstError or err )

        if positives > 0:
            return ( True, firstError )

        else:
            return ( Criteria.UNKNOWN, firstError ) if self.fuzzy( ctx ) else ( None, firstError )


class Any( All ):


    def __call__( self, ctx ):
        firstError = None
        for one in self.many:
            ans, err = one( ctx )
            """
            1. True
            2. False
            3. UNKNOWN: in error state but fuzzy is True
            4. None: in error state and fuzzy is False
            """
            if ans == True:
                return ( ans, firstError or err )

            elif ans == False:
                firstError = firstError or err

            else:
                if self.fuzzy( ctx ):
                    firstError = firstError or err

                else:
                    return ( ans, firstError or err )

        return ( False, firstError )


class And( All ):


    @property
    def left( self ):
        return self._many[ 0 ]

    @property
    def right( self ):
        return self._many[ 1 ]

    def __init__( self, left, right ):
        super( And, self ).__init__( left, right )


class Or( Any ):


    @property
    def left( self ):
        return self._many[ 0 ]

    @property
    def right( self ):
        return self._many[ 1 ]

    def __init__( self, left, right ):
        super( Or, self ).__init__( left, right )


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


