from lstc import AtomicSentence, SentenceInterpreter

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

def is_equal(name, args, world = None):
    if not isinstance(name, str):
        raise TypeError()
    assert name in AtomicSentence._predicate_set
    if not isinstance(args, list):
        raise TypeError()
    if len(args) != AtomicSentence.get_arity(name):
        raise ValueError()
    assert len(args) == 2
    if not isinstance(args[0], int)\
        or not isinstance(args[1], int):
        raise TypeError()
    return args[0] == args[1]

def op_not(li):
    if not isinstance(li, list):
        raise TypeError()
    if len(li) != 1:
        raise ValueError()
    if not isinstance(li[0], bool):
        raise TypeError()
    return not li[0]

def op_or(li):
    if not isinstance(li, list):
        raise TypeError()
    if len(li) == 0:
        raise ValueError()
    if not isinstance(li[0], bool):
        raise TypeError()
    return True in li

def op_and(li):
    if not isinstance(li, list):
        raise TypeError()
    if len(li) == 0:
        raise ValueError()
    if not isinstance(li[0], bool):
        raise TypeError()
    return not False in li

def test_sentence_interpreter():
    AtomicSentence.clear()
    AtomicSentence.add_predicate("=",2)
    for i in range(10):
        AtomicSentence.add_constant(str(i))
    SentenceInterpreter.clear() 
    for i in range(10):
        SentenceInterpreter.set_constant_interpretation(str(i), i)
    SentenceInterpreter.set_predicate_interpretation("=", is_equal)
    SentenceInterpreter.set_operator_interpretation("not", op_not)
    SentenceInterpreter.set_operator_interpretation("or",  op_or)
    SentenceInterpreter.set_operator_interpretation("and", op_and)
    testcase_list = [
        ["=(0,0)", True],
        ["=(1,0)", False],
        [("or",  "=(0,0)", "=(1,0)"), True],
        [("and", "=(0,0)", "=(1,0)"), False],
        [("and", "=(0,0)", ("not", "=(1,0)")), True],
        [("or", ("not", "=(0,0)"), "=(1,0)"), False],
    ]
    for sentence, expected in testcase_list:
        assert SentenceInterpreter.interprete(sentence) == expected
    SentenceInterpreter.clear() 
    AtomicSentence.clear()

