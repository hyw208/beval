import ast
import numbers
import operator
import collections


class Const(object):

    UNKNOWN = "__UNKNOWN__"
    ERROR = "__ERROR__"

    Bool = "Bool"
    Eq = "Eq"
    NotEq = "NotEq"
    LtE = "LtE"
    Lt = "Lt"
    GtE = "GtE"
    Gt = "Gt"
    Between = "Between"
    In = "In"
    NotIn = "NotIn"
    And = "And"
    Or = "Or"
    All = "All"
    Any = "Any"
    Not = "Not"
    Ctx = "Ctx"
    Visitor = "Visitor"
    Universal = "Universal"

    True_ = "True"
    False_ = "False"
    None_ = "None"

    fuzzy = "fuzzy"

    getitem = "__getitem__"
    eval_ = "eval"

    true = "true"
    false = "false"
    universal = "*"

    eq_ = "=="
    ne_ = "!="
    lt_ = "<"
    le_ = "<="
    gt_ = ">"
    ge_ = ">="
    in_ = "in"
    not_in_ = "not in"
    and_ = "and"
    or_ = "or"
    not_ = "not"

    func = "func"
    args = "args"
    keywords = "keywords"
    kwargs = "kwargs"


def to_criteria(expr):
    return criteria_class.instance(Const.Visitor, expr).go()


def safe_monad(func, *args, **kwargs):
    try:
        obj = func(*args, **kwargs)

    except Exception as err:
        return None, err

    else:
        return obj, None


def quote(obj):
    return ("'%s'" if isinstance(obj, str) else "%s") % obj


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
            outcomes = fuzzy_types if (hasattr(ctx, Const.fuzzy) and ctx.fuzzy) or fuzzy else std_types
            (ans, err) = func(criteria, ctx, fuzzy)

            if ans not in outcomes:
                raise AssertionError("unexpected outcome type '%s' for criteria '%s'" % (type(ans), type(criteria)))

            else:
                return ans, err

        return decorated

    return assert_outcomes_d


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

        raise KeyError("cannot find key '%s'" % key)

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
        if hasattr(self._one, Const.getitem) and key in self._one:
            return self._one[key]

        elif isinstance(key, str) and hasattr(self._one, key):
            obj = getattr(self._one, key)
            return obj() if callable(obj) else obj

        elif isinstance(key, str) and hasattr(self, key):
            obj = getattr(self, key)
            return obj() if callable(obj) else obj

        else:
            raise KeyError("cannot find key '%s'" % key)


class Criteria(object):

    @assert_outcomes_d_w_a([True, False, Const.ERROR], [True, False, Const.UNKNOWN])
    def __call__(self, obj, fuzzy=False):
        ctx = obj if isinstance(obj, Ctx) else criteria_class.instance(Const.Ctx, obj, fuzzy)
        return self.eval(ctx)

    def compare(self, ctx, key, op, left, right):
        func = SyntaxAstCallExtender.find_comparator(type(right))
        return safe_monad(func, ctx, key, op, left, right) if func else safe_monad(op, left, right)

    def eval(self, ctx):
        raise NotImplementedError

    def fuzzy(self, ctx):
        return ctx.fuzzy

    def __init__(self, stack=True):
        self._stack = list() if stack else None

    def size(self):
        return len(self._stack)

    def _push(self, item):
        self._stack.append(item)

    def _pop(self):
        return self._stack.pop()

    def Bool(self, key):
        c = criteria_class.instance(Const.Bool, key)
        self._push(c)
        return self

    def Eq(self, key, right):
        c = criteria_class.instance(Const.Eq, key, right)
        self._push(c)
        return self

    def NotEq(self, key, right):
        c = criteria_class.instance(Const.NotEq, key, right)
        self._push(c)
        return self

    def LtE(self, key, right):
        c = criteria_class.instance(Const.LtE, key, right)
        self._push(c)
        return self

    def Lt(self, key, right):
        c = criteria_class.instance(Const.Lt, key, right)
        self._push(c)
        return self

    def GtE(self, key, right):
        c = criteria_class.instance(Const.GtE, key, right)
        self._push(c)
        return self

    def Gt(self, key, right):
        c = criteria_class.instance(Const.Gt, key, right)
        self._push(c)
        return self

    def Between(self, lower, key, upper, lower_op=operator.le, upper_op=operator.lt):
        c = criteria_class.instance(Const.Between, lower, key, upper, lower_op, upper_op)
        self._push(c)
        return self

    def In(self, key, *right):
        c = criteria_class.instance(Const.In, key, *right)
        self._push(c)
        return self

    def NotIn(self, key, *right):
        c = criteria_class.instance(Const.NotIn, key, *right)
        self._push(c)
        return self

    def And(self):
        (r, l) = (self._pop(), self._pop())
        c = criteria_class.instance(Const.And, l, r)
        self._push(c)
        return self

    def Or(self):
        (r, l) = (self._pop(), self._pop())
        c = criteria_class.instance(Const.Or, l, r)
        self._push(c)
        return self

    def All(self):
        c = criteria_class.instance(Const.All, *self._stack)
        self._stack = [c]
        return self

    def Any(self):
        c = criteria_class.instance(Const.Any, *self._stack)
        self._stack = [c]
        return self

    def Not(self):
        c = criteria_class.instance(Const.Not, self._pop())
        self._push(c)
        return self

    def Done(self):
        if self.size() != 1:
            raise SyntaxError("more items on stack still, %s" % self.size())

        return self._stack.pop()


class Bool(Criteria):

    @property
    def key(self):
        return self._key

    def __init__(self, key):
        super(Bool, self).__init__(stack=False)
        self._key = types_supported_as_key(self, key)

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            if isinstance(obj, bool):
                return obj, None

            elif isinstance(obj, numbers.Number):
                return bool(obj), None

            elif isinstance(obj, str) and obj.lower() in (Const.true, Const.false,):
                return True if obj.lower() == Const.true else False, None

            else:
                return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, TypeError("%s is not supported" % type(obj))

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err

    def __str__(self):
        return "%s" % self._key


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
        super(Eq, self).__init__(stack=False)
        self._op = op
        self._key = types_supported_as_key(self, key)
        self._right = right

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            (obj_, err_) = self.compare(ctx, self._key, self._op, obj, self._right)

            if err_ is None:
                return obj_, None

            else:
                return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err_

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err

    def __str__(self):
        return "%s %s %s" % (self._key, operator_ser_symbol.lookup(self._op), quote(self._right))


class NotEq(Eq):

    @property
    def op(self):
        return operator.ne

    def __init__(self, key, right):
        super(NotEq, self).__init__(key, right)

    def eval(self, ctx):
        (obj, err) = super(NotEq, self).eval(ctx)
        return not obj if obj in (True, False,) else obj, err

    def __str__(self):
        return "%s %s %s" % (self._key, operator_ser_symbol.lookup(self.op), quote(self._right))


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
        super(Between, self).__init__(stack=False)
        self._lower = lower
        self._lower_op = lower_op
        self._key = types_supported_as_key(self, key)
        self._upper_op = upper_op
        self._upper = upper

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            (obj_, err_) = self.compare(ctx, self._key, self._lower_op, self._lower, obj)

            if obj_ in (True,):
                (obj2_, err2_) = self.compare(ctx, self._key, self._upper_op, obj, self._upper)

                if err2_ is None:
                    return obj2_, None

                else:
                    return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err2_

            else:
                if err_ is None:
                    return obj_, None

                else:
                    return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err_

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err

    def __str__(self):
        return "%s %s %s %s %s" % \
            (self._lower, operator_ser_symbol.lookup(self._lower_op),
                self._key, operator_ser_symbol.lookup(self._upper_op), self._upper)


class In(Eq):

    def __init__(self, key, *right):
        super(In, self).__init__(key, right)

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            negative = 0
            first_error = None

            for one in self.right:
                (obj_, err_) = self.compare(ctx, self._key, self._op, obj, one)
                if obj_ in (True,):
                    return obj_, first_error or err_

                elif obj_ in (False,):
                    negative += 1
                    first_error = first_error or err_

                else:
                    if self.fuzzy(ctx):
                        first_error = first_error or err_

                    else:
                        return Const.ERROR, first_error or err_

            if negative > 0:
                return False, first_error

            else:
                return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, first_error

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err

    def __str__(self):
        return "%s %s (%s,)" % (self._key, operator_ser_symbol.lookup(Const.in_), ",".join(quote(one) for one in self._right))


class NotIn(In):

    def __init__(self, key, *right):
        super(NotIn, self).__init__(key, *right)

    def eval(self, ctx):
        (obj, err) = super(NotIn, self).eval(ctx)
        return not obj if obj in (True, False,) else obj, err

    def __str__(self):
        return "%s %s (%s,)" % (self._key, operator_ser_symbol.lookup(Const.not_in_), ",".join(quote(one) for one in self._right))


class All(Criteria):

    @property
    def many(self):
        return self._many

    def __init__(self, *many):
        super(All, self).__init__(stack=False)
        for one in many:
            if not isinstance(one, Criteria):
                raise TypeError("%s is not supported" % type(one))

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
                    return Const.ERROR, first_error or err

        if positive > 0:
            return True, first_error

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, first_error

    def __str__(self):
        return (" %s " % operator_ser_symbol.lookup(Const.and_)).join(str(one) for one in self._many)


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
                    return Const.ERROR, first_error or err

        if negative > 0:
            return False, first_error

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, first_error

    def __str__(self):
        return (" %s " % operator_ser_symbol.lookup(Const.or_)).join( str(one) for one in self._many)


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
        return "(%s %s %s)" % (self.left, operator_ser_symbol.lookup(Const.and_), self.right)


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
        return "(%s %s %s)" % (self.left, operator_ser_symbol.lookup(Const.or_), self.right)


class Not(Criteria):

    @property
    def one(self):
        return self._one

    def __init__(self, one):
        if not isinstance(one, Criteria):
            raise TypeError("%s is not supported" % type(one))

        super(Not, self).__init__(stack=False)
        self._one = one

    def eval(self, ctx):
        (obj, err) = self._one(ctx)
        return not obj if obj in (True, False,) else obj, err

    def __str__(self):
        return "%s (%s)" % (operator_ser_symbol.lookup(Const.not_), str(self._one))


class Universal(object):

    def __eq__(self, other):
        return True

    def __str__(self):
        return "'%s'" % Const.universal


class bEvalVisitor(ast.NodeVisitor):

    def __init__(self, expr):
        self.expr = expr
        self.data = list()

    def visit_Expression(self, node):
        self.visit(node.body)
        obj = self.data.pop()
        criteria = obj if isinstance(obj, Criteria) else criteria_class.instance(Const.Bool, obj)
        self.data.append(criteria)

    def visit_BoolOp(self, node):
        if type(node.op) not in (ast.And, ast.Or,):
            raise SyntaxError("%s is not supported" % type(node.op))

        many = list()
        for value in node.values:
            self.visit(value)
            obj = self.data.pop()
            criteria = obj if isinstance(obj, Criteria) else criteria_class.instance(Const.Bool, obj)
            many.append(criteria)

        if isinstance(node.op, ast.And):
            cls = (criteria_class.lookup(Const.And) if len(many) == 2 else criteria_class.lookup(Const.All))

        else:
            cls = (criteria_class.lookup(Const.Or) if len(many) == 2 else criteria_class.lookup(Const.Any))

        criteria = cls(*many)
        self.data.append(criteria)

    def visit_UnaryOp(self, node):
        if type(node.op) not in (ast.Not,):
            raise SyntaxError("%s is not supported" % type(node.op))

        self.visit(node.operand)
        obj = self.data.pop()
        criteria = obj if isinstance(obj, Criteria) else criteria_class.instance(Const.Bool, obj)

        cls = criteria_class.lookup(ast_op_to_criteria.lookup(type(node.op)))
        criteria = cls(criteria)
        self.data.append(criteria)

    def visit_Compare(self, node):
        if len(node.ops) not in (1, 2,):
            raise SyntaxError("ast.Compare with more than 2 ops: %s is not supported" % node)

        (_, left), (_, ops), (_, comps) = ast.iter_fields(node)
        self.visit(left)
        left = self.data.pop()

        comparators = list()
        for comparator in comps:
            self.visit(comparator)
            comparators.append(self.data.pop())

        if len(ops) == 1:
            right = comparators[0]
            cls = criteria_class.lookup(ast_op_to_criteria.lookup(type(ops[0])))
            criteria = cls(left, *right) if type(right) in (list, tuple,) else cls(left, right)
            self.data.append(criteria)

        else:
            lower = left
            lower_op = ast_op_to_operator.lookup(type(ops[0]))
            one = comparators[0]
            upper_op = ast_op_to_operator.lookup(type(ops[1]))
            upper = comparators[1]
            criteria = criteria_class.instance(Const.Between, lower, one, upper, lower_op, upper_op)
            self.data.append(criteria)

    def visit_Call(self, node):
        fields = {k: v for k, v in ast.iter_fields(node) if v}

        self.visit(fields[Const.func])
        name, args, kwargs = self.data.pop(), list(), collections.OrderedDict()

        func = SyntaxAstCallExtender.find_deserializer(name)
        if not func:
            raise SyntaxError("%s is not supported" % name)

        if Const.args in fields:
            for arg in fields[Const.args]:
                self.visit(arg)
                args.append(self.data.pop())

        if Const.keywords in fields:
            for keyword in fields[Const.keywords]:
                (_, key), (_, value) = ast.iter_fields(keyword)
                self.visit(value)
                kwargs[key] = self.data.pop()

        if Const.kwargs in fields:
            (_, knodes), (_, vnodes) = ast.iter_fields(fields[Const.kwargs])
            for knode, vnode in zip(knodes, vnodes):
                self.visit(knode)
                key = self.data.pop()
                self.visit(vnode)
                value = self.data.pop()
                kwargs[key] = value

        obj = func(*args, **kwargs)
        self.data.append(obj)

    def visit_Tuple(self, node):
        values = list()
        for e in node.elts:
            self.visit(e)
            values.append(self.data.pop())

        self.data.append(values)

    def visit_Num(self, node):
        self.data.append(node.n)

    def visit_Str(self, node):
        self.data.append(universal if node.s == Const.universal else node.s)

    def visit_Name(self, node):
        if node.id == Const.True_:
            id_ = True

        elif node.id == Const.False_:
            id_ = False

        elif node.id == Const.None_:
            id_ = None

        else:
            id_ = node.id

        self.data.append(id_)

    def go(self):
        node = ast.parse(self.expr, mode=Const.eval_)
        self.visit(node)
        return self.data.pop()


class SyntaxAstCallExtender(object):

    deserializers = dict()
    comparators = dict()

    @classmethod
    def register(cls, extender):
        SyntaxAstCallExtender.deserializers[extender.name()] = extender
        SyntaxAstCallExtender.comparators[extender.type()] = extender

    @classmethod
    def find_deserializer(cls, name):
        extender = SyntaxAstCallExtender.deserializers.get(name, None)
        if extender:
            return extender.deserialize

    @classmethod
    def find_comparator(cls, type_):
        extender = SyntaxAstCallExtender.comparators.get(type_, None)
        if extender:
            return extender.compare

    def name(self):
        raise NotImplementedError

    def deserialize(self, *args, **kwargs):
        raise NotImplementedError

    def type(self):
        raise NotImplementedError

    def compare(self, ctx, key, op, left, right):
        raise NotImplementedError


class Config(object):

    @property
    def config(self):
        return self._config

    def __init__(self, config):
        self._config = config

    def lookup(self, key):
        return self._config.get(key, None)

    def override(self, key, obj):
        self._config[key] = obj

    def instance(self, key, *args, **kwargs):
        obj = self.lookup(key)
        return obj(*args, **kwargs)


operator_ser_symbol = Config({
    operator.eq: Const.eq_,
    operator.ne: Const.ne_,
    operator.lt: Const.lt_,
    operator.le: Const.le_,
    operator.gt: Const.gt_,
    operator.ge: Const.ge_,
    Const.in_: Const.in_,
    Const.not_in_: Const.not_in_,
    Const.not_: Const.not_,
    Const.and_: Const.and_,
    Const.or_: Const.or_,
})


ast_op_to_criteria = Config({
    ast.Eq: Const.Eq,
    ast.NotEq: Const.NotEq,
    ast.Lt: Const.Lt,
    ast.LtE: Const.LtE,
    ast.Gt: Const.Gt,
    ast.GtE: Const.GtE,
    ast.In: Const.In,
    ast.NotIn: Const.NotIn,
    ast.Not: Const.Not,
})


ast_op_to_operator = Config({
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
})


criteria_class = Config({
    Const.Bool: Bool,
    Const.Eq: Eq,
    Const.NotEq: NotEq,
    Const.Between: Between,
    Const.Gt: Gt,
    Const.GtE: GtE,
    Const.Lt: Lt,
    Const.LtE: LtE,
    Const.In: In,
    Const.NotIn: NotIn,
    Const.And: And,
    Const.All: All,
    Const.Or: Or,
    Const.Any: Any,
    Const.Not: Not,
    Const.Ctx: Ctx,
    Const.Visitor: bEvalVisitor,
    Const.Universal: Universal,
})


cTrue = criteria_class.instance(Const.Bool, True)
cFalse = criteria_class.instance(Const.Bool, False)
universal = criteria_class.instance(Const.Universal)
