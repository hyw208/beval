########################################
boolean expression evaluator
########################################
The utility is designed to capture bool expressions as criteria objects and perform evaluations against one to many in-memory objects. For example, given an instance or a list of objects of type Car or dict or basically any type containing the info below. See tests.test_helper for a list of car objects.

+--------+----------+-----------+-----------+-------------+-----------+--------------+
|  make  |  type    |  maxprice |  mpgcity  |   mpghiway  |  airbags  |   drivetrain |
+========+==========+===========+===========+=============+===========+==============+
|  Acura |  Small   |  18.8     |  25       |   31        |  None     |   Front      |
+--------+----------+-----------+-----------+-------------+-----------+--------------+
|  Ford  |  Compact |  12.2     |  22       |   27        |  None     |   Front      |
+--------+----------+-----------+-----------+-------------+-----------+--------------+


===========================
to define a criteria
===========================
To define a search criteria where "make" is "Acura", "type" is "Small" and "drivetrain" is "Front", there are 3 options,

option 1, type the string boolean expression and convert it to a criteria object

    >>> search_criteria = to_criteria( "make == 'Acura' and type == 'Small' and drivetrain == 'Front'" )

option 2, create a criteria in polish notation, sort of

    >>> search_criteria = Criteria().Eq("make", "Acura").Eq("type", "Small").Eq("drivetrain", "Front").All().Done()

option 3, or simply compose the criteria object

    >>> search_criteria = All(Eq("make", "Acura"), Eq("type", "Small"), Eq("drivetrain", "Front"))


===========================
to eval a criteria against an object
===========================
To evaluate the search criteria, there are also a few options available,

option 1, invoke the __call__ method with an underlying object or a ctx object wrapping around the underlying

    >>> (ans, err) = search_criteria(acura_small)
    (True, None)
    >>> (ans, err) = search_criteria(Ctx(acura_small, False))
    (True, None)

option 2, call the eval method, with a ctx object

    >>> (ans, err) = search_criteria.eval(Ctx(acura_small, fuzzy=False))
    (True, None)

option 3, define a simple function to change the return type and behavior

    >>> def true_or_false(criteria, obj):
            (ans, err) = criteria(obj)
            if ans in (Criteria.UNKNOWN, Criteria.ERROR,):
                raise err
            else:
                return ans
    >>> true_or_false(search_criteria, acura_small)
    (True, None)


===========================
transform the representation of a criteria between text and object
===========================
A criteria object can be serialized to a string and de-serialized back to an object,

    >>> expr = "make == 'Acura' and type == 'Small' and drivetrain == 'Front'"
    >>> criteria = to_criteria(expr)
    >>> str(criteria)
    "make == 'Acura' and type == 'Small' and drivetrain == 'Front'"


===========================
to change the evaluation behavior of a criteria
===========================
When dealing with a bag of objects with inconsistent api or various data quality, the fuzzy search option can be turned on. When the flag is turned on, evaluator continues to evaluate the next criteria despite error accessing non-existent property or exception thrown during comparison. For instance, given an expression with an non-existent property 'cpu':

    >>> search_criteria = to_criteria( "cpu == 'Intel' and make == 'Acura' and type == 'Small' and drivetrain == 'Front'" )
    >>> search_criteria(acura_small, fuzzy=False)
    ('__ERROR__', KeyError('cannot find item cpu'))
    >>> search_criteria(acura_small, fuzzy=True)
    (True, KeyError('cannot find item cpu'))

During evaluation against the "All" criteria, it starts with the first "Eq" criteria where cpu == 'Intel'. Since the car object, acura_small, doesn't have such property, missing 'cpu' KeyError is raised and then ignored. "All" criteria evalution continues to check the following "Eq" criteria where type == 'Small' and so on. The resulting err object, if any, is the first error/exception encountered.




