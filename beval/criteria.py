import ast
import numbers
import operator


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
    visit = "visit"

    True_ = "True"
    False_ = "False"
    None_ = "None"

    fuzzy = "fuzzy"

    getitem = "__getitem__"
    eval_ = "eval"

    true = "true"
    false = "false"

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
        return Const.UNKNOWN if fuzzy else Const.ERROR, err


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

        else:
            raise KeyError("cannot find key '%s'" % key)


class Criteria(object):

    @assert_outcomes_d_w_a([True, False, Const.ERROR], [True, False, Const.UNKNOWN])
    def __call__(self, obj, fuzzy=False):
        ctx = obj if isinstance(obj, Ctx) else criteria_class.instance(Const.Ctx, obj, fuzzy)
        return self.eval(ctx)

    def compare(self, ctx, key, op, left, right):
        return safe(self.fuzzy(ctx), op, left, right)

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
        super(Eq, self).__init__()
        self._op = op
        self._key = types_supported_as_key(self, key)
        self._right = right

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            (obj_, err_) = self.compare(ctx, self._key, self._op, obj, self._right)
            return obj_, err_

        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err

    def __str__(self):
        return "%s %s %s" % (self._key, operator_ser_symbol.lookup(self._op), quote(self._right))


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
        super(Between, self).__init__()
        self._lower = lower
        self._lower_op = lower_op
        self._key = types_supported_as_key(self, key)
        self._upper_op = upper_op
        self._upper = upper

    def eval(self, ctx):
        (obj, err) = safe_monad(access, ctx, self._key)

        if err is None:
            (obj_, err_) = self.compare(ctx, self._key, self._lower_op, self._lower, obj)

            if obj_ in (True, ):
                (obj2_, err2_) = self.compare(ctx, self._key, self._upper_op, obj, self._upper)
                return obj2_, err2_

            else:
                return obj_, err_
        else:
            return Const.UNKNOWN if self.fuzzy(ctx) else Const.ERROR, err

    def __str__(self):
        return "%s %s %s %s %s" % \
            (self._lower, operator_ser_symbol.lookup(self._lower_op),
                self._key, operator_ser_symbol.lookup(self._upper_op), self._upper)


class In(Eq):

    def __init__(self, key, *right):
        super(In, self).__init__(key, right)

    def compare(self, ctx, key, op, left, right):
        func = in_syntax_extender_cmp_func.lookup(type(right))
        return safe_monad(func, ctx, key, op, left, right) if func else safe_monad(op, left, right)

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
        super(All, self).__init__()
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

        super(Not, self).__init__()
        self._one = one

    def eval(self, ctx):
        (obj, err) = self._one(ctx)
        return not obj if obj in (True, False,) else obj, err

    def __str__(self):
        return "%s (%s)" % (operator_ser_symbol.lookup(Const.not_), str(self._one))


def quote(obj):
    return ("'%s'" if isinstance(obj, str) else "%s") % obj


def to_criteria(text):
    data = []
    criteria_class.instance(Const.visit, ast.parse(text, mode=Const.eval_), data)
    return data.pop()


def visit(node, data):

    if isinstance(node, ast.Expression):
        visit(node.body, data)
        if len(data) != 1:
            raise SyntaxError("multiple expression nodes, %s, are not supported" % len(data))

        obj = data.pop()
        data.append(obj if isinstance(obj, Criteria) else criteria_class.instance(Const.Bool, obj))
        return

    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
            values = []
            for value in node.values:
                visit(value, data)
                obj = data.pop()
                values.append(obj if isinstance(obj, Criteria) else criteria_class.instance(Const.Bool, obj))

            if isinstance(node.op, ast.And):
                cls = (criteria_class.lookup(Const.And) if len(values) == 2 else criteria_class.lookup(Const.All))
            else:
                cls = (criteria_class.lookup(Const.Or) if len(values) == 2 else criteria_class.lookup(Const.Any))

            data.append(cls(*values))
            return

        else:
            raise SyntaxError("%s is not supported" % type(node.op))

    if isinstance(node, ast.Compare):
        visit(node.left, data)
        left = data.pop()

        if len(node.ops) == 1:
            op = node.ops[0]
            cls = criteria_class.lookup(ast_op_to_criteria.lookup(type(op)))

            comparator = node.comparators[0]
            visit(comparator, data)
            right = data.pop()

            if cls in (criteria_class.lookup(Const.In), criteria_class.lookup(Const.NotIn),):
                c = cls(left, *right) if type(right) in (list, tuple,) else cls(left, right)
            else:
                c = cls(left, right)

            data.append(c)
            return

        elif len(node.ops) == 2:
            lower = left

            op = node.ops[0]
            lower_op = ast_op_to_operator.lookup(type(op))

            comparator = node.comparators[0]
            visit(comparator, data)
            one = data.pop()

            op = node.ops[1]
            upper_op = ast_op_to_operator.lookup(type(op))

            comparator = node.comparators[1]
            visit(comparator, data)
            upper = data.pop()

            between = criteria_class.instance(Const.Between, lower, one, upper, lower_op, upper_op)
            data.append(between)
            return

        else:
            raise SyntaxError("ast.Compare with more than 2 ops: %s is not supported" % node)

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            visit(node.operand, data)
            obj = data.pop()
            criteria = obj if isinstance(obj, Criteria) else criteria_class.instance(Const.Bool, obj)

            cls = criteria_class.lookup(ast_op_to_criteria.lookup(type(node.op)))
            data.append(cls(criteria))
            return

        else:
            raise SyntaxError("%s is not supported" % type(node.op))

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
        if node.id == Const.True_:
            id_ = True

        elif node.id == Const.False_:
            id_ = False

        elif node.id == Const.None_:
            id_ = None

        else:
            id_ = node.id

        data.append(id_)
        return

    if isinstance(node, ast.keyword):
        (_, key), (_, value) = ast.iter_fields(node)
        visit(value, data)
        data.append((key, data.pop()))
        return

    if isinstance(node, ast.Call):
        fields = {k: v for k, v in ast.iter_fields(node) if v}

        visit(fields[Const.func], data)
        func_name = data.pop()
        func = in_syntax_extender_deser_func.lookup(func_name)
        if not func:
            raise SyntaxError("%s is not supported" % func_name)

        args = list()
        if Const.args in fields:
            for arg in fields[Const.args]:
                visit(arg, data)
                args.append(data.pop())

        keywords = {}
        if Const.keywords in fields:
            for keyword in fields[Const.keywords]:
                visit(keyword, data)
                k, v = data.pop()
                keywords[k] = v

        kwargs = {}
        if Const.kwargs in fields:
            (_, knodes), (_, vnodes) = ast.iter_fields(fields[Const.kwargs])
            keys = list()
            for knode in knodes:
                visit(knode, data)
                keys.append(data.pop())
            values = list()
            for vnode in vnodes:
                visit(vnode, data)
                values.append(data.pop())
            kwargs = {k: v for k, v in zip(keys, values)}

        keywords.update(kwargs)
        data.append(func(*args, **keywords))
        return


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
    Const.visit: visit,
})


cTrue = criteria_class.instance(Const.Bool, True)
cFalse = criteria_class.instance(Const.Bool, False)


in_syntax_extender_cmp_func = Config({})
in_syntax_extender_deser_func = Config({})


