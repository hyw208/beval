import ast
import numbers
import operator


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


def types_supported_as_key(criteria, key):
    if isinstance(key, str) or isinstance(key, bool) or isinstance(key, numbers.Number):
        return key

    else:
        raise TypeError("%s is not supported as key for %s" % type(key), type(criteria))


def assert_outcomes_d_w_a(std_types, fuzzy_types):
    """ remove this decorator after fully tested with use cases """
    def assert_outcomes_d(func):

        def decorated(criteria, ctx, fuzzy=False):
            outcomes = fuzzy_types if (hasattr(ctx, 'fuzzy') and ctx.fuzzy) or fuzzy else std_types
            (ans, err) = func(criteria, ctx, fuzzy)

            if ans not in outcomes:
                raise AssertionError("unexpected outcome type '%s' for criteria '%s'" % (type(ans), type(criteria)))

            else:
                return ans, err

        return decorated

    return assert_outcomes_d


class Criteria(object):

    UNKNOWN = '__UNKNOWN__'
    ERROR = '__ERROR__'

    @assert_outcomes_d_w_a([True, False, ERROR], [True, False, UNKNOWN])
    def __call__(self, obj, fuzzy=False):
        ctx = obj if isinstance(obj, Ctx) else Ctx(obj, fuzzy)
        return self.eval(ctx)

    def eval(self, ctx):
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

    def Bool(self, key):
        c = Bool(key)
        self._push(c)
        return self

    def Eq(self, key, right):
        c = Eq(key, right)
        self._push(c)
        return self

    def NotEq(self, key, right):
        c = NotEq(key, right)
        self._push(c)
        return self

    def LtE(self, key, right):
        c = LtE(key, right)
        self._push(c)
        return self

    def Lt(self, key, right):
        c = Lt(key, right)
        self._push(c)
        return self

    def GtE(self, key, right):
        c = GtE(key, right)
        self._push(c)
        return self

    def Gt(self, key, right):
        c = Gt(key, right)
        self._push(c)
        return self

    def Between(self, lower, key, upper, lower_op=operator.le, upper_op=operator.lt):
        c = Between(lower, key, upper, lower_op, upper_op)
        self._push(c)
        return self

    def In(self, key, *right):
        c = In(key, *right)
        self._push(c)
        return self

    def NotIn(self, key, *right):
        c = NotIn(key, *right)
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
    def key(self):
        return self._key

    def __init__(self, key):
        self._key = types_supported_as_key(self, key)

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            if isinstance(obj, bool):
                return obj, None

            elif isinstance(obj, numbers.Number):
                return bool(obj), None

            elif isinstance(obj, str) and obj.lower() in ('true', 'false',):
                return True if obj.lower() == 'true' else False, None

            else:
                return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, TypeError("%s not supported" % type(obj))

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err

    def __str__(self):
        return "%s" % self._key


cTrue = Bool(True)

cFalse = Bool(False)


class Eq(Criteria):

    @property
    def key(self):
        return self._key

    @property
    def right(self):
        return self._right

    @property
    def op(self):
        return self._op

    def __init__(self, key, right, op=operator.eq):
        self._op = op
        self._key = types_supported_as_key(self, key)
        self._right = right

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            (obj_, err_) = safe(self.fuzzy(ctx), self._op, obj, self._right)
            return obj_, err_

        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err

    def __str__(self):
        return "%s %s %s" % (self._key, OP_TO_TEXT_MAP[self._op], quote(self._right))


class NotEq(Eq):

    def __init__(self, key, right):
        super(NotEq, self).__init__(key, right, operator.ne)


class Lt(Eq):

    def __init__(self, key, right):
        super(Lt, self).__init__(key, right, operator.lt)


class LtE(Eq):

    def __init__(self, key, right):
        super(LtE, self).__init__(key, right, operator.le)


class Gt(Eq):

    def __init__(self, key, right):
        super(Gt, self).__init__(key, right, operator.gt)


class GtE(Eq):

    def __init__(self, key, right):
        super(GtE, self).__init__(key, right, operator.ge)


class Between(Criteria):

    @property
    def lower(self):
        return self._lower

    @property
    def lower_op(self):
        return self._lower_op

    @property
    def key(self):
        return self._key

    @property
    def upper_op(self):
        return self._upper_op

    @property
    def upper(self):
        return self._upper

    def __init__(self, lower, key, upper, lower_op=operator.le, upper_op=operator.lt):
        self._lower = lower
        self._lower_op = lower_op
        self._key = types_supported_as_key(self, key)
        self._upper_op = upper_op
        self._upper = upper

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            (obj_, err_) = safe(self.fuzzy(ctx), self._lower_op, self._lower, obj)

            if obj_ in (True, ):
                (obj2_, err2_) = safe(self.fuzzy(ctx), self._upper_op, obj, self._upper)
                return obj2_, err2_

            else:
                return obj_, err_
        else:
            return Criteria.UNKNOWN if self.fuzzy(ctx) else Criteria.ERROR, err

    def __str__(self):
        return "%s %s %s %s %s" % (self._lower, OP_TO_TEXT_MAP[self._lower_op], self._key, OP_TO_TEXT_MAP[self._upper_op], self._upper)


class In(Eq):

    def __init__(self, key, *right):
        super(In, self).__init__(key, right)

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

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

    def __str__(self):
        return "%s in (%s,)" % (self._key, ",".join(quote(one) for one in self._right))


class NotIn(In):

    def __init__(self, key, *right):
        super(NotIn, self).__init__(key, *right)

    def eval(self, ctx):
        (obj, err) = super(NotIn, self).eval(ctx)
        return not obj if obj in (True, False,) else obj, err

    def __str__(self):
        return "%s not in (%s,)" % (self._key, ",".join(quote(one) for one in self._right))


class All(Criteria):

    @property
    def many(self):
        return self._many

    def __init__(self, *many):
        for one in many:
            if not isinstance(one, Criteria):
                raise TypeError("%s not supported" % type(one))

        self._many = many

    def eval(self, ctx):
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

    def __str__(self):
        return "%s" % " and ".join( str(one) for one in self._many )


class Any(All):

    def eval(self, ctx):
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

    def __str__(self):
        return "%s" % " or ".join( str(one) for one in self._many )


class And(All):

    @property
    def left(self):
        return self._many[0]

    @property
    def right(self):
        return self._many[1]

    def __init__(self, left, right):
        super(And, self).__init__(left, right)

    def __str__(self):
        return "(%s and %s)" % (self.left, self.right)


class Or(Any):

    @property
    def left(self):
        return self._many[0]

    @property
    def right(self):
        return self._many[1]

    def __init__(self, left, right):
        super(Or, self).__init__(left, right)

    def __str__(self):
        return "(%s or %s)" % (self.left, self.right)


class Not(Criteria):

    @property
    def one(self):
        return self._one

    def __init__(self, one):
        if not isinstance(one, Criteria):
            raise TypeError("%s not supported" % type(one))

        self._one = one

    def eval(self, ctx):
        (obj, err) = self._one(ctx)
        return not obj if obj in (True, False,) else obj, err

    def __str__(self):
        return "not (%s)" % str(self._one)


OP_TO_TEXT_MAP = {
    operator.eq: "==",
    operator.ne: "!=",
    operator.lt: "<",
    operator.le: "<=",
    operator.gt: ">",
    operator.ge: ">=",
}


AST_OP_TO_CRITERIA_MAP = {
    ast.Eq: Eq,
    ast.NotEq: NotEq,
    ast.Lt: Lt,
    ast.LtE: LtE,
    ast.Gt: Gt,
    ast.GtE: GtE,
    ast.Not: Not,
    ast.In: In,
    ast.NotIn: NotIn,
}


AST_OP_TO_OPERATOR_MAP = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


def quote(obj):
    return ("'%s'" if isinstance(obj, str) else "%s") % obj


def to_criteria(text):
    data = []
    visit(ast.parse(text, mode='eval'), data)
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
        if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
            values = []
            for value in node.values:
                visit(value, data)
                obj = data.pop()
                values.append(obj if isinstance(obj, Criteria) else Bool(obj))

            cls = (And if len(values) == 2 else All) \
                        if isinstance(node.op, ast.And) else \
                            (Or if len(values) == 2 else Any)

            data.append(cls(*values))
            return

        else:
            raise SyntaxError("do not support %s" % type(node.op))

    if isinstance(node, ast.Compare):
        visit(node.left, data)
        left = data.pop()

        if len(node.ops) == 1:
            op = node.ops[0]
            cls = AST_OP_TO_CRITERIA_MAP[type(op)]

            comparator = node.comparators[0]
            visit(comparator, data)
            right = data.pop()

            c = cls(left, right) if cls not in (In, NotIn, ) else cls(left, *right)
            data.append(c)
            return

        elif len(node.ops) == 2:
            lower = left

            op = node.ops[0]
            lower_op = AST_OP_TO_OPERATOR_MAP[type(op)]

            comparator = node.comparators[0]
            visit(comparator, data)
            one = data.pop()

            op = node.ops[1]
            upper_op = AST_OP_TO_OPERATOR_MAP[type(op)]

            comparator = node.comparators[1]
            visit(comparator, data)
            upper = data.pop()

            between = Between( lower, one, upper, lower_op, upper_op )
            data.append(between)
            return

        else:
            raise SyntaxError("do not support ast.Compare with more than 2 ops: %s" % node)

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            visit(node.operand, data)
            obj = data.pop()
            criteria = obj if isinstance(obj, Criteria) else Bool(obj)

            cls = AST_OP_TO_CRITERIA_MAP[type(node.op)]
            data.append(cls(criteria))
            return

        else:
            raise SyntaxError("do not support %s" % type(node.op))

    if isinstance(node, ast.Tuple):
        values = []
        for elt in node.elts:
            visit(elt, data)
            values.append(data.pop())
        data.append(values)
        return

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

