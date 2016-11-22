########################################
boolean expression evaluator
########################################
The utility is designed to capture bool expressions as criteria objects and perform evaluations over one to many in-memory objects. For example, given an instance or a list of Car objects, see tests.test_helper for a list of car objects:

+--------+----------+-----------+-----------+-------------+-----------+--------------+
|  make  |  type    |  maxprice |  mpgcity  |   mpghiway  |  airbags  |   drivetrain |
+========+==========+===========+===========+=============+===========+==============+
|  Acura |  Small   |  18.8     |  25       |   31        |  None     |   Front      |
+--------+----------+-----------+-----------+-------------+-----------+--------------+
|  Ford  |  Compact |  12.2     |  22       |   27        |  None     |   Front      |
+--------+----------+-----------+-----------+-------------+-----------+--------------+


===========================
criteria creation
===========================
To define a search criteria where "make" is "Acura", "type" is "Small" and "drivetrain" is "Front", there are 3 options,

option 1, type the string expression and convert it to a criteria object

    >>> search_criteria = to_criteria( "make == 'Acura' and type == 'Small' and drivetrain == 'Front'" )

option 2, specify a criteria in polish notation, sort of

    >>> search_criteria = Criteria().Eq("make", "Acura").Eq("type", "Small").Eq("drivetrain", "Front").All().Done()

option 3, or just compose the criteria object

    >>> search_criteria = All(Eq("make", "Acura"), Eq("type", "Small"), Eq("drivetrain", "Front"))


===========================
criteria evaluation against an object
===========================
To evaluate the criteria, there are also a few options,

option 1, invoke __call__ method with an underlying object or a ctx object

    >>> (ans, err) = search_criteria(acura_small)
    >>> (ans, err) = search_criteria(Ctx(acura_small, False))

option 2, invoke eval method, with a ctx object

    >>> (ans, err) = search_criteria.eval(Ctx(acura_small, fuzzy=False))

option 3, change return type and behavior

    >>> def true_or_false(criteria, obj):
    >>>      (ans, err) = criteria(obj)
    >>>      if ans in (Criteria.UNKNOWN, Criteria.ERROR,):
    >>>          raise err
    >>>      else:
    >>>          return ans
    >>>
    >>> ans = true_or_false(search_criteria, acura_small)


===========================
criteria representations
===========================
Criteria objects can be serialized to string representations and back to objects,

    >>> bool_expr = "make == 'Acura' and type == 'Small' and drivetrain == 'Front'"
    >>> search_criteria = to_criteria(bool_expr)
    >>> bool_expr = str(search_criteria)


===========================
criteria behavior and control flag
===========================
When dealing with objects with inconsistent api or data quality issues, the fuzzy search option can be turned on. Fuzzy search will continue to evaluate the next criteria despite error accessing non-existent property or field, and it will ignore any exception thrown during comparison. For instance, given a modified search criteria below:

    >>> search_criteria = to_criteria( "cpu == 'Intel' and make == 'Acura' and type == 'Small' and drivetrain == 'Front'" )
    >>> (ans, err) = search_criteria(acura_small, fuzzy=True)

The fuzzy search option is turned on and it will encounter error accessing attribute/property/field "abc", this error is ignored, and evalution continues to check the next criteria type == 'Small'.




