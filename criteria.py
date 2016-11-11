import ast
import numbers
import operator


OP_TO_TEXT_MAP = {
    operator.eq: "==",
    operator.lt: "<",
    operator.le: "<=",
    operator.gt: "<",
    operator.ge: "<=",
}


def quote(obj):
    if isinstance(obj, str):
        return "'%s'" % obj
    else:
        return "%s" % obj


def safe_monad(func, *args, **kwargs):
    try:
        obj = func(*args, **kwargs)
    except Exception as err:
        return None, err
    else:
        return obj, None


def safe(fuzzy, func, *args, **kwargs):
    (obj, err) = safe_monad(func, *args, **kwargs)

    if err is None:
        return obj, None
    else:
        return Criteria.UNKNOWN if fuzzy else Criteria.ERROR, err


def access(ctx, key):
    return ctx[key]


class Criteria(object):

    UNKNOWN = '__UNKNOWN__'
    ERROR = '__ERROR__'

    def __call__(self, ctx):
        raise NotImplementedError

    def fuzzy(self, ctx):
        return ctx.fuzzy

    def __init__(self):
        self._stack = []

    def size(self):
        return len(self._stack)

    def _push(self, item):
        self._stack.append(item)

    def _pop(self):
        return self._stack.pop()

    def Eq(self, left, right):
        c = Eq(left, right)
        self._push(c)
        return self

    def NotEq(self, left, right):
        c = NotEq(left, right)
        self._push(c)
        return self

    def LtE(self, left, right):
        c = LtE(left, right)
        self._push(c)
        return self

    def Lt(self, left, right):
        c = Lt(left, right)
        self._push(c)
        return self

    def GtE(self, left, right):
        c = GtE(left, right)
        self._push(c)
        return self

    def Gt(self, left, right):
        c = Gt(left, right)
        self._push(c)
        return self

    def Between(self, lower, one, upper):
        c = Between(lower, one, upper)
        self._push(c)
        return self

    def In(self, left, *right):
        c = In(left, *right)
        self._push(c)
        return self

    def NotIn(self, left, *right):
        c = NotIn(left, *right)
        self._push(c)
        return self

    def And(self):
        (r, l) = (self._pop(), self._pop())
        c = And(l, r)
        self._push(c)
        return self

    def Or(self):
        (r, l) = (self._pop(), self._pop())
        c = Or(l, r)
        self._push(c)
        return self

    def All(self):
        c = All(*self._stack)
        self._stack = [c]
        return self

    def Any(self):
        c = Any(*self._stack)
        self._stack = [c]
        return self

    def Not(self):
        c = Not(self._pop())
        self._push(c)
        return self

    def Done(self):
        if self.size() != 1:
            raise SyntaxError('more items on stack still, %s' % self.size())

        return self._stack.pop()


class AbstractCtx(object):

    def __getitem__(self, key):
        (obj, err) = safe_monad(self.key, key)
        if err is None:
            return obj

        if isinstance(key, bool) or isinstance(key, numbers.Number):
            return key

        (obj, err) = safe_monad(ast.literal_eval, key)
        if err is None:
            return obj

        raise KeyError('cannot find item %s' % key)

    def key(self, key):
        raise NotImplementedError


class Ctx(AbstractCtx):

    @property
    def one(self):
        return self._one

    @property
    def fuzzy(self):
        return self._fuzzy

    def __init__(self, one, fuzzy=False):
        self._one = one
        self._fuzzy = fuzzy

    def key(self, key):
        if hasattr(self._one, "__getitem__") and key in self._one:
            return self._one[key]

        elif isinstance(key, str) and hasattr(self._one, key):
            obj = getattr(self._one, key)
            return obj() if callable(obj) else obj

        else:
            raise KeyError("cannot find item %s" % key)


class Bool(Criteria):

    @property
    def one(self):
        return self._one

    def __init__(self, one):
        if not (isinstance(one, str) or isinstance(one, bool)):
            raise TypeError("%s not supported" % type(one))

        self._one = one

    def __call__(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._one)

        if err is None:
            if isinstance(obj, bool):
                return obj, None

            elif isinstance(obj, str) and obj.lower() in ('true', 'false',):
                return True if obj.lower() == 'true' else False, None

            else:
                return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, TypeError("%s not supported" % type(obj))

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err


cTrue = Bool(True)

cFalse = Bool(False)


class Eq(Criteria):

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def op(self):
        return self._op

    def __init__(self, left, right, op=operator.eq):
        self._left = left
        self._right = right
        self._op = op

    def __call__(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._left)

        if err is None:
            (obj_, err_) = safe(self.fuzzy(ctx), self._op, obj, self._right)
            return obj_, err_

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err

    def __str__(self):
        return "%s %s %s" % (self._left, OP_TO_TEXT_MAP[self._op], quote(self._right))


class NotEq(Eq):

    def __init__(self, left, right):
        super(NotEq, self).__init__(left, right, operator.ne)


class Lt(Eq):

    def __init__(self, left, right):
        super(Lt, self).__init__(left, right, operator.lt)


class LtE(Eq):

    def __init__(self, left, right):
        super(LtE, self).__init__(left, right, operator.le)


class Gt(Eq):

    def __init__(self, left, right):
        super(Gt, self).__init__(left, right, operator.gt)


class GtE(Eq):

    def __init__(self, left, right):
        super(GtE, self).__init__(left, right, operator.ge)


class Between(Criteria):

    @property
    def lower(self):
        return self._lower

    @property
    def lower_op(self):
        return self._lower_op

    @property
    def one(self):
        return self._one

    @property
    def upper_op(self):
        return self._upper_op

    @property
    def upper(self):
        return self._upper

    def __init__(self, lower, one, upper, lower_op=operator.le, upper_op=operator.lt):
        self._lower = lower
        self._lower_op = lower_op
        self._one = one
        self._upper_op = upper_op
        self._upper = upper

    def __call__(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._one)

        if err is None:
            (obj_, err_) = safe(self.fuzzy(ctx), self._lower_op, self._lower, obj)

            if obj_ in (True, ):
                (obj2_, err2_) = safe(self.fuzzy(ctx), self._upper_op, obj, self._upper)
                return obj2_, err2_

            else:
                return obj_, err_
        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err


class In(Eq):

    def __init__(self, left, *right):
        super(In, self).__init__(left, right)

    def __call__(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._left)

        if err is None:
            negative = 0
            first_error = None

            for one in self.right:
                (obj_, err_) = safe_monad(self._op, obj, one)

                if obj_ in (True,):
                    return obj_, first_error or err_

                elif obj_ in (False,):
                    negative += 1
                    first_error = first_error or err_

                else:
                    if self.fuzzy(ctx):
                        first_error = first_error or err_

                    else:
                        return Criteria.ERROR, first_error or err_

            if negative > 0:
                return False, first_error

            else:
                return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, first_error

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err


class NotIn(In):

    def __init__(self, left, *right):
        super(NotIn, self).__init__(left, *right)

    def __call__(self, ctx):
        (obj, err) = super(NotIn, self).__call__(ctx)
        return not obj if obj in (True, False,) else obj, err


class All(Criteria):

    @property
    def many(self):
        return self._many

    def __init__(self, *many):
        for one in many:
            if not isinstance(one, Criteria):
                raise TypeError("%s not supported" % type(one))

        self._many = many

    def __call__(self, ctx):
        positive = 0
        first_error = None

        for one in self._many:
            (obj, err) = one(ctx)

            if obj in (True,):
                positive += 1
                first_error = first_error or err

            elif obj in (False,):
                return obj, first_error or err

            else:
                if self.fuzzy(ctx):
                    first_error = first_error or err

                else:
                    return Criteria.ERROR, first_error or err

        if positive > 0:
            return True, first_error

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, first_error


class Any(All):

    def __call__(self, ctx):
        negative = 0
        first_error = None

        for one in self._many:
            (obj, err) = one(ctx)

            if obj in (True,):
                return obj, first_error or err

            elif obj in (False,):
                negative += 1
                first_error = first_error or err

            else:
                if self.fuzzy(ctx):
                    first_error = first_error or err

                else:
                    return Criteria.ERROR, first_error or err

        if negative > 0:
            return False, first_error

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, first_error


class And(All):

    @property
    def left(self):
        return self._many[0]

    @property
    def right(self):
        return self._many[1]

    def __init__(self, left, right):
        super(And, self).__init__(left, right)


class Or(Any):

    @property
    def left(self):
        return self._many[0]

    @property
    def right(self):
        return self._many[1]

    def __init__(self, left, right):
        super(Or, self).__init__(left, right)


class Not(Criteria):

    @property
    def one(self):
        return self._one

    def __init__(self, one):
        if not isinstance(one, Criteria):
            raise TypeError("%s not supported" % type(one))

        self._one = one

    def __call__(self, ctx):
        (obj, err) = self._one(ctx)
        return not obj if obj in (True, False,) else obj, err


AST_OP_TO_CRITERIA_MAP = {
    ast.Eq: Eq,
    ast.NotEq: NotEq,
    ast.Lt: Lt,
    ast.LtE: LtE,
    ast.Gt: Gt,
    ast.GtE: GtE,
    "Between": Between,
    ast.In: In,
    ast.NotIn: NotIn,
}


def toCriteria(text):
    data = []
    node = ast.parse(text, mode='eval')
    visit(node, data)
    return data.pop()


def visit(node, data):
    if isinstance(node, ast.Expression):
        visit(node.body, data)
        if len(data) != 1:
            raise SyntaxError("do not support multiple expression nodes, %s" % len(data))

        obj = data.pop()
        data.append(obj if isinstance(obj, Criteria) else Bool(obj))
        return

    if isinstance(node, ast.BoolOp):
        raise NotImplementedError

    if isinstance(node, ast.Compare):
        visit(node.left, data)
        left = data.pop()

        if len(node.ops):
            op = node.ops[0]
            cls = AST_OP_TO_CRITERIA_MAP[type(op)]

            comparator = node.comparators[0]
            visit(comparator, data)
            right = data.pop()

            c = cls(left, right)
            data.append(c)
            return

        elif len(node.ops) == 2:
            lowerOp = node.ops[0]
            lower = node.comparators[0]

            upperOp = node.ops[1]
            upper = node.comparator[1]
            print

        else:
            raise Exception("do not support ast.Compare with more than 2 ops: %s" % node)

    if isinstance(node, ast.UnaryOp):
        raise NotImplementedError

    if isinstance(node, ast.Num):
        data.append(node.n)
        return

    if isinstance(node, ast.Str):
        data.append(node.s)
        return

    if isinstance(node, ast.Name):
        if node.id == 'True':
            id = True

        elif node.id == 'False':
            id = False

        else:
            id = node.id

        data.append(id)
        return
