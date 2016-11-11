import operator
import ast


OP_TO_TEXT_MAP = {
    operator.eq: "==",
    operator.lt: "<",
    operator.le: "<=",
    operator.gt: "<",
    operator.ge: "<=",
}


def quote( obj ):
    if isinstance( obj, str ):
        return "'%s'" % obj

    else:
        return "%s" % obj


def safe_monad( func, *args, **kwargs ):
    try:
        obj = func( *args, **kwargs )

    except Exception as err:
        return ( None, err )

    else:
        return ( obj, None )


def safe( fuzzy, func, *args, **kwargs ):
    ans, err = safe_monad( func, *args, **kwargs )

    if err is None:
        return ( ans, None )

    else:
        return ( Criteria.UNKNOWN, err ) if fuzzy else ( Criteria.ERROR, err )


def access( ctx, item ):
    return ctx[ item ]


class Criteria( object ):

    UNKNOWN = "__UNKNOWN__"
    ERROR   = "__ERROR__"

    def __call__( self, ctx ):
        raise NotImplementedError

    def fuzzy( self, ctx ):
        return ctx.fuzzy

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


    @property
    def target( self ):
        return self._target

    @target.setter
    def target( self, target ):
        self._target = target

    @property
    def fuzzy( self ):
        return self._fuzzy

    @fuzzy.setter
    def fuzzy( self, fuzzy ):
        self._fuzzy = fuzzy

    def __init__( self, target, fuzzy = False ):
        self._target = target
        self._fuzzy = fuzzy

    def __getitem__( self, item ):
        if hasattr( self.target, "__getitem__" ) and item in self.target:
            return self.target[ item ]

        elif hasattr( self.target, item ):
            obj = getattr( self.target, item )
            return obj() if callable( obj ) else obj

        else:
            raise KeyError( "Cannot get %s out of object of type %s" % ( item, type( self.target ) ) )


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


True_  = Bool( True )
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
        obj, err = safe_monad( access, ctx, self.left )

        if err is None:
            obj_, err_ = safe( self.fuzzy( ctx ), self.op, obj, self.right )
            """
            True
            False
            Criteria.UNKNOWN
            Criteria.ERROR
            """
            return ( obj_, err_ )

        else:
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( Criteria.ERROR, err )

    def __str__( self ):
        text = "%s %s %s" % ( self.left, OP_TO_TEXT_MAP[ self.op ], quote( self.right ) )
        return text


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

        if err is None:
            obj_, err_ = safe( self.fuzzy( ctx ), self.lowerOp, self.lower, obj )
            if obj_ == True:
                obj2_, err2_ = safe( self.fuzzy( ctx ), self.upperOp, obj, self.upper )
                return ( obj2_, err2_ )

            else:
                return ( obj_, err_ )
        else:
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( Criteria.ERROR, err )


class In( Eq ):


    def __init__( self, left, *right ):
        super( In, self ).__init__( left, right )

    def __call__( self, ctx ):
        obj, err = safe_monad( access, ctx, self.left )

        if err is None:
            negatives = 0
            firstError = None
            for one in self.right:
                obj_, err_ = safe_monad( self.op, obj, one )

                if obj_ == True:
                    return ( obj_, firstError or err_ )

                elif obj_ == False:
                    negatives += 1
                    firstError = firstError or err_

                else:
                    if self.fuzzy( ctx ):
                        firstError = firstError or err_

                    else:
                        return ( Criteria.ERROR, firstError or err_ )

            """ no positive hit """
            if negatives > 0:
                return ( False, firstError )

            else:
                return ( Criteria.UNKNOWN, firstError ) if self.fuzzy( ctx ) else ( Criteria.ERROR, firstError )

        else:
            return ( Criteria.UNKNOWN, err ) if self.fuzzy( ctx ) else ( Criteria.ERROR, err )



class NotIn( In ):


    def __init__( self, left, *right ):
        super( NotIn, self ).__init__( left, *right )

    def __call__( self, ctx ):
        ans, err = super( NotIn, self ).__call__( ctx )
        """
        True
        False
        Criteria.UNKNOWN
        Criteria.ERROR
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
            True
            False
            Criteria.UNKNOWN
            Criteria.ERROR
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
                    return ( Criteria.ERROR, firstError or err )

        if positives > 0:
            return ( True, firstError )

        else:
            return ( Criteria.UNKNOWN, firstError ) if self.fuzzy( ctx ) else ( Criteria.ERROR, firstError )


class Any( All ):


    def __call__( self, ctx ):
        negatives = 0
        firstError = None
        for one in self.many:
            ans, err = one( ctx )
            """
            True
            False
            Criteria.UNKNOWN
            Criteria.ERROR
            """
            if ans == True:
                return ( ans, firstError or err )

            elif ans == False:
                negatives += 1
                firstError = firstError or err

            else:
                if self.fuzzy( ctx ):
                    firstError = firstError or err

                else:
                    return ( Criteria.ERROR, firstError or err )

        if negatives > 0:
            return ( False, firstError )

        else:
            return ( Criteria.UNKNOWN, firstError ) if self.fuzzy( ctx ) else ( Criteria.ERROR, firstError )


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
        Criteria.ERROR
        """
        if ans in ( True, False ):
            return ( not ans, err )

        else:
            return ( ans, err )


AST_OP_TO_CRITERIA_MAP = {
    ast.LtE: Le,

}


def visit( node, data ):
    if isinstance( node, ast.Expression ):
        visit( node.body, data )

    if isinstance( node, ast.BoolOp ): # and, or
        print

    if isinstance( node, ast.Compare ):
        name = visit( node.left, data )

        if len( node.ops ) == 1:
            op = node.ops[ 0 ]
            comparator = node.comparators[ 0 ]
            print

        elif len( node.ops ) == 2:
            lowerOp = node.ops[ 0 ]
            lower = node.comparators[ 0 ]

            upperOp = node.ops[ 1 ]
            upper = node.comparator[ 1 ]
            print

        else:
            raise Exception( "do not support ast.Compare with more than 2 ops: %s" % node )


    if isinstance( node, ast.UnaryOp ):
        # not
        pass

    if isinstance( node, ast.Str ):
        data.append( node.s )

    if isinstance( node, ast.Name ):
        if node.id == 'True':
            id = True

        elif node.id == 'False':
            id = False

        else:
            id = node.id

        data.append( id )