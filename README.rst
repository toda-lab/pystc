pystc: A simple but extensible Python module for sentences
==========================================================

Introduction
============
A *sentence* is an atomic sentence or a (compound) sentence.
An *atomic sentence* consists of a *predicate* and *constants* the predicate has
as its arguments.
There is no variable, no function.
The number of arguments of a predicate is called the *arity* of the predicate.
A compound sentence can be obtained by joining sentences with *connectives*.

``pystc`` is a simple but extensible Python module for sentences.
It provides functionality to define sentences as you like 
by adding constants, predicates, and connectives, whether logical or non-logical.
Constants, predicates, and connectives can be introduced by specifying
their names and how they are associated with other well-defined objects or
functions.

Installation
============

.. code:: shell-session

    $ pip install pystc

Usage
=====

Let us first create atomic sentences that can be built from a predicate ``=``
and constants ``T``, ``F``, 

.. code:: python

    from pystc import AtomicSentence

    # Let us add predicate "=" so that the arity for it is 2.
    AtomicSentence.add_predicate("=",2) 
    AtomicSentence.add_constant("T")
    AtomicSentence.add_constant("F")

    # Now, sentences are ready to create.
    s1 = AtomicSentence("=","T","T")
    s2 = AtomicSentence("=","T","F")
    s3 = AtomicSentence("=","F","T")

    assert str(s2) == "=(T,F)"
    assert AtomicSentence.read("=(T,F)") == s2

Let us next construct compound sentences.
A ``Sentence`` in ``pystc`` module is simply a recursive type defined to be:

.. code:: python

    Sentence = Union[str, AtomicSentence, Tuple["Sentence"]]

Although it is loosely defined for simplicity, 
sentences are implicitly expected to fall into one of the following cases:

1. An AtomicSentence object, say ``s2``.
1. The string representation of an AtomicSentence object, say ``"=(T,F)"``.
1. A tuple such that the initial entry is a connective name and the other entries are Sentence objects, say ``("&", s2, ("!", s2))``.

As the connective names ``"&"`` and ``"!"`` appears just above, 
let us introduce these connectives in the following codeblock
and inteprete sentences.

.. code:: python

    from pystc import SentenceConverter

    # Let us set an atomic sentence type and how each symbol is interpreted.
    SentenceConverter.set_atom_type(AtomicSentence)
    SentenceConverter.set_constant_destination("T", True)
    SentenceConverter.set_constant_destination("F", False)
    SentenceConverter.set_predicate_destination("=", lambda li,w: li[0]==li[1])
    SentenceConverter.set_connective_destination("&",lambda li,w: not False in li)
    SentenceConverter.set_connective_destination("|",lambda li,w: True in li)
    SentenceConverter.set_connective_destination("!",lambda li,w: not li[0])

    assert SentenceConverter.convert(s2) == False
    assert SentenceConverter.convert("=(T,F)") == False
    assert SentenceConverter.convert(("&", s2, ("!", s2))) == False
    assert SentenceConverter.convert(("&", "=(T,F)", ("!", s2))) == False

For another example of usage, let us convert sentences into strings in infix
notation.

.. code:: python

    # Clear all class variables
    SentenceConverter.clear()

    SentenceConverter.set_atom_type(AtomicSentence)
    SentenceConverter.set_constant_destination("T", "T")
    SentenceConverter.set_constant_destination("F", "F")
    SentenceConverter.set_predicate_destination("=", lambda li,w: f"{li[0]}={li[1]}")
    SentenceConverter.set_connective_destination("&",lambda li,w: "("+" & ".join(li)+")")
    SentenceConverter.set_connective_destination("|",lambda li,w: "("+" | ".join(li)+")")
    SentenceConverter.set_connective_destination("!",lambda li,w: "!"+li[0])

    assert SentenceConverter.convert("=(T,F)") == "T=F"
    assert SentenceConverter.convert(("&", s2, ("!", s2))) == "(T=F & !T=F)"

Let us not forget to clear class variables after everything is finished.

.. code:: python

    SentenceConverter.clear()
    AtomicSentence.clear()


Bugs/Requests/Discussions
=========================

Please report bugs and requests from `GitHub Issues <https://github.com/toda-lab/pystc/issues>`__ , and 
ask questions from `GitHub Discussions <https://github.com/toda-lab/pystc/discussions>`__ .

License
=======

Please see `LICENSE <https://github.com/toda-lab/pystc/blob/main/LICENSE>`__ .
