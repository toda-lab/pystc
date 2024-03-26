from lstc import AtomicSentence, SentenceConverter

def test_atomic_sentence():
    testcase_list = [\
        ("x","A","B"),
        ("x","A","A"),
        ("x","B","A"),
        ("x","A","B"),
    ]

    AtomicSentence.clear()
    AtomicSentence.add_predicate("x", 2)
    AtomicSentence.add_constant("A")
    AtomicSentence.add_constant("B")

    S = set()
    for testcase in testcase_list:
        S.add(AtomicSentence(*testcase))
    assert len(S) == 3 
    assert set(map(str, S)) == {"x(A,B)", "x(A,A)", "x(B,A)"}
    AtomicSentence.clear()

def test_add_predicate():
    testcase_list = [\
        ("x",2,True),\
        ("Z",1,False),\
        ("0x",1,True),\
        ("_a",1,True),\
        ("-1",1,True),\
    ]

    AtomicSentence.clear()
    for args in testcase_list:
        AtomicSentence.add_predicate(args[0],args[1],observable=args[2])
    assert AtomicSentence._predicate_set\
        == set([args[0].strip() for args in testcase_list])
    for args in testcase_list:
        assert AtomicSentence.get_arity(args[0])     == args[1]
        assert AtomicSentence.is_observable(args[0]) == args[2]
    AtomicSentence.clear()
        
def test_add_constant():
    testcase_list = [\
        "+", "_a", "aa", "A" ,"-", "+",
    ]

    AtomicSentence.clear()
    for constant in testcase_list:
        AtomicSentence.add_constant(constant)
    assert AtomicSentence._constant_set == set(testcase_list)
    AtomicSentence.clear()

def test_read():
    testcase_list = [\
        "x(A,B)",
        "x(B,B)",
        "x(B,A)",
        " x(A,B)",
        "x(A,B) ",
        "x (A,B)",
        "x ( A,B)",
        "x (A, B)",
    ]

    AtomicSentence.clear()
    AtomicSentence.add_predicate("x", 2)
    AtomicSentence.add_constant("A")
    AtomicSentence.add_constant("B")
    S = set()
    for text in testcase_list:
        S.add(AtomicSentence.read(text))

    assert len(S) == 3
    assert set(map(str, S)) == {"x(A,B)", "x(B,B)", "x(B,A)"}
    for obj in S:
        assert AtomicSentence.read(str(obj)) == obj
    AtomicSentence.clear()

def test_sentence_converter():
    AtomicSentence.clear()
    AtomicSentence.add_predicate("=",2)
    for i in range(10):
        AtomicSentence.add_constant(str(i))
    # Evaluate sentences in predicate logic.
    SentenceConverter.clear() 
    for i in range(10):
        SentenceConverter.set_constant_destination(str(i), i)
    SentenceConverter.set_predicate_destination("=", is_equal)
    SentenceConverter.set_connective_destination("not", logical_not)
    SentenceConverter.set_connective_destination("or",  logical_or)
    SentenceConverter.set_connective_destination("and", logical_and)
    testcase_list = [
        ["=(0,0)",                             True],
        ["=(1,0)",                             False],
        [("or",  "=(0,0)", "=(1,0)"),          True],
        [("and", "=(0,0)", "=(1,0)"),          False],
        [("and", AtomicSentence("=","0","0"),\
            ("not", AtomicSentence("=","1","0"))), True],
        [("or", ("not", "=(0,0)"), AtomicSentence("=","1","0")),  False],
    ]
    for sentence, expected in testcase_list:
        assert SentenceConverter.convert(sentence) == expected
    # Convert sentences to strings in infix notation.
    SentenceConverter.clear() 
    for i in range(10):
        SentenceConverter.set_constant_destination(str(i), i)
    SentenceConverter.set_predicate_destination("=", to_equal_str)
    SentenceConverter.set_connective_destination("not", to_not_str)
    SentenceConverter.set_connective_destination("or",  to_or_str)
    SentenceConverter.set_connective_destination("and", to_and_str)
    testcase_list = [
        ["=(0,0)",                             "0=0"],
        ["=(1,0)",                             "1=0"],
        [("or",  "=(0,0)", "=(1,0)"),          "(0=0 | 1=0)"],
        [("and", "=(0,0)", "=(1,0)"),          "(0=0 & 1=0)"],
        [("and", "=(0,0)", ("not", "=(1,0)")), "(0=0 & !1=0)"],
        [("or", ("not", "=(0,0)"), "=(1,0)"),  "(!0=0 | 1=0)"],
    ]
    for sentence, expected in testcase_list:
        assert SentenceConverter.convert(sentence) == expected
    SentenceConverter.clear() 
    AtomicSentence.clear()

def is_equal(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    for x in args:
        if not isinstance(x, int):
            raise TypeError()
    return args[0] == args[1]

def logical_not(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    if not isinstance(args[0], bool):
        raise TypeError()
    return not args[0]

def logical_or(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    for x in args:
        if not isinstance(x, bool):
            raise TypeError()
    return True in args 

def logical_and(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    for x in args:
        if not isinstance(x, bool):
            raise TypeError()
    return not False in args

def to_equal_str(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    for x in args:
        if not isinstance(x, int):
            raise TypeError()
    return f"{args[0]}={args[1]}"

def to_not_str(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    if not isinstance(args[0], str):
        raise TypeError()
    return "!" + args[0] 

def to_or_str(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    for x in args:
        if not isinstance(x, str):
            raise TypeError()
    return "(" + " | ".join(args) + ")"

def to_and_str(args, world = None):
    if not isinstance(args, list):
        raise TypeError()
    for x in args:
        if not isinstance(x, str):
            raise TypeError()
    return "(" + " & ".join(args) + ")"
