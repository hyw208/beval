########################################
Boolean expression evaluator
########################################
The utility is designed to capture bool expressions as criteria objects and perform evaluations against one to many in-memory objects. For example, given an instance or a list of objects of type Car or dict or basically any type containing the info below. See tests.test_helper for a list of car objects.

+---------+----------+-----------+-----------+-------------+-----------+--------------+
|  make   |  type    |  maxprice |  mpgcity  |   mpghiway  |  airbags  |  drivetrain  |
+=========+==========+===========+===========+=============+===========+==============+
|  Acura  |  Small   |  18.8     |  25       |   31        |  None     |  Front       |
+---------+----------+-----------+-----------+-------------+-----------+--------------+
|  Ford   |  Compact |  12.2     |  22       |   27        |  None     |  Front       |
+---------+----------+-----------+-----------+-------------+-----------+--------------+
|  Subaru |  Compact |  22.7     |  23       |   30        |  Driver   |  All         |
+---------+----------+-----------+-----------+-------------+-----------+--------------+


===========================
To define a simple criteria
===========================
To define an "Eq" criteria and evaluate against a car object of type dict. Object to be evaluated can be of any type as long as it has the property or method.

    >>> subaru = {"make": "Subaru", "type": "Compact", "mpgcity": 30} <-- define a simple car of type dict
    >>> acura = {"make": "Acura", "type": "Small", "mpgcity": 25}
    >>> from beval.criteria import Eq, Between
    >>> eq = Eq("make", "Subaru")
    >>> eq(subaru)
    (True, None)
    >>> eq(acura)
    (False, None)

To define a "Between" criteria,

    >>> btw = Between(28, "mpgcity", 32)
    >>> btw(subaru)
    (True, None)
    >>> btw(acura)
    (False, None)

===========================
More on defining a criteria
===========================
To define a search criteria for cars where "make" is "Acura", "type" is "Small" and "drivetrain" is "Front", there are 3 options,

option 1, type a string boolean expression and convert it to a criteria object

    >>> from beval.criteria import Const, Criteria, to_criteria, Eq, All
    >>> search_criteria = to_criteria( "make == 'Acura' and type == 'Small' and drivetrain == 'Front'" )

option 2, create a criteria in polish notation, sort of

    >>> search_criteria = Criteria().Eq("make", "Acura").Eq("type", "Small").Eq("drivetrain", "Front").All().Done()

option 3, or simply compose a criteria object

    >>> search_criteria = All(Eq("make", "Acura"), Eq("type", "Small"), Eq("drivetrain", "Front"))


===========================
More on evaluating against an object
===========================
To evaluate a search criteria, there are also a few options available,

option 1, invoke the __call__ method with an underlying object or a ctx object wrapping around the underlying

    >>> (ans, err) = search_criteria(acura_small)
    (True, None)
    >>> (ans, err) = search_criteria(Ctx(acura_small, False))
    (True, None)

option 2, call the eval method, with a ctx object

    >>> (ans, err) = search_criteria.eval(Ctx(acura_small, fuzzy=False))
    (True, None)

option 3, define a simple function in order to change the return type and behavior

    >>> def evaluate(criteria, obj, fuzzy=False):
            (ans, err) = criteria(obj, fuzzy)
            if ans in (Const.UNKNOWN, Const.ERROR,):
                raise err
            else:
                return ans
    >>> evaluate(search_criteria, acura_small)
    True


===========================
To transform the representation of a criteria
===========================
A criteria object can be serialized to a string and de-serialized back to an object,

    >>> expr = "make == 'Acura' and type == 'Small' and drivetrain == 'Front'"
    >>> expr
    "make == 'Acura' and type == 'Small' and drivetrain == 'Front'"
    >>> search_criteria = to_criteria(expr)
    >>> str(search_criteria)
    "make == 'Acura' and type == 'Small' and drivetrain == 'Front'"


===========================
To change the evaluation behavior of a criteria
===========================
When dealing with a bag of objects with inconsistent api or various data quality, the fuzzy search option can be turned on. When the flag is on, evaluator continues to evaluate the next criteria despite error accessing non-existent property or exception thrown during comparison. For instance, given an expression with an non-existent property 'cpu':

    >>> search_criteria = to_criteria( "cpu == 'Intel' and make == 'Acura' and type == 'Small' and drivetrain == 'Front'" )
    >>> type(search_criteria)
    beval.criteria.All
    >>> str(search_criteria.many[0]) <-- check the 1st criteria inside
    "cpu == 'Intel'"
    >>> str(search_criteria.many[1]) <-- check the 2nd criteria inside
    "make == 'Acura'"
    >>> search_criteria(acura_small, fuzzy=False)
    ('__ERROR__', KeyError('cannot find item cpu'))
    >>> search_criteria(acura_small, fuzzy=True)
    (True, KeyError('cannot find item cpu'))

During evaluation of the "All" criteria, evaluator starts with the 1st "Eq" criteria where cpu == 'Intel'. For the car object, acura_small, it doesn't have a 'cpu' property, therefore a KeyError is raised and captured. "All" criteria evaluator then continues to check the next "Eq" criteria where type == 'Small' and so on. The resulting err object, if any, is the very first error/exception encountered.


===========================
To filter a list of objects
===========================
A simple way with list comprehension,

    >>> cars = [{"make": "Subaru", "drivetrain": "All"}, {"make": "Acura", "drivetrain": "Front"}, {"make": "Ford", "drivetrain": "Front"}]
    >>> search_criteria = to_criteria( "make == 'Acura' and drivetrain == 'Front'" )
    >>> matched = [car for car in cars if True in search_criteria(car)]
    >>> len(matched)
    1
    >>> matched[0]
    {'drivetrain': 'Front', 'make': 'Acura'}

Or use the built-in filter, create a predicate function that returns True or False,

    >>> def predicate(obj):
            (ans, err) = search_criteria(obj)
            if ans in (Const.UNKNOWN, Const.ERROR,):
                raise err
            else:
                return ans
    >>> matched = filter(predicate, cars)
    >>> len(matched)
    1
    >>> matched[0]
    {'drivetrain': 'Front', 'make': 'Acura'}

Or create a generic predicate function and use functools.partial to bind arguments,

    >>> from functools import partial
    >>> def predicate(criteria, fuzzy, obj):
            (ans, err) = criteria(obj, fuzzy)
            if ans in (Const.UNKNOWN, Const.ERROR,):
                raise err
            else:
                return ans
    >>> predicate2 = partial(predicate, search_criteria, False)
    >>> matched = filter(predicate2, cars)
    >>> len(matched)
    1
    >>> matched[0]
    {'drivetrain': 'Front', 'make': 'Acura'}


===========================
A bit of info on Ctx
===========================
TBA


===========================
List of available criteria classes
===========================
* Bool
* Eq
* NotEq
* Between
* Gt
* GtE
* Lt
* LtE
* In
* NotIn
* And
* All
* Or
* Any
* Not




