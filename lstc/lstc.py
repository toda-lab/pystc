from typing import Tuple, Set, Dict, Union, Callable, Any, Optional, Final

import re

class AtomicSentence:
    """Class of Sentences without variables, logical connectives and quantifiers."""

    _constant_set       = set()
    """Set of constants."""
    _predicate_set      = set()
    """Set of predicates."""
    _arity_dict         = {}
    """Dictionary that maps predicate to arity (number of arguments)."""
    _observability_dict = {}
    """Dictionary that maps predicate to truth value about observability."""
    _unique_table       = {}
    """Dictionary that maps string representation of sentence to sentence."""
    _name_pattern: Final[str] = r"[a-zA-Z0-9_+-@]+"
    """Name patterns for constants and predicates."""

    @classmethod
    def add_predicate(cls,\
        predicate: str, arity: int, observable: bool = True) -> None:
        """Adds a predicate.

        Nothing is done if predicate has been already added.

        Args:
            predicate: A predicate name.
            arity: The number of arguments a predicate has.
            observable: Whether it is an observable predicate or not.

        Returns:
            None

        Raises:
            TypeError:  if predicaite is not a str.
            TypeError:  if arity is not an int.
            TypeError:  if observable is not a bool.
            ValueError: if predicate does not "fullmatch" name pattern.
            ValueError: if arity is negative.
        """
        if not isinstance(predicate, str):
            raise TypeError()
        if not isinstance(arity, int):
            raise TypeError()
        if not isinstance(observable, bool):
            raise TypeError()
        if re.fullmatch(cls._name_pattern, predicate) == None:
            raise ValueError(f"{predicate} does not match name pattern.")
        if arity < 0:
            raise ValueError(f"invalid arity: {arity}")
        if predicate in cls._predicate_set:
            return
        cls._predicate_set.add(predicate)
        cls._arity_dict[predicate] = arity
        cls._observability_dict[predicate] = observable

    @classmethod
    def add_constant(cls, constant: str) -> None:
        """Adds a constant.

        Nothing is done if constant has been already done.

        Args:
            constant: A constant name.

        Returns:
            None

        Raises:
            TypeError:  if constant is not a str.
            ValueError: if constant does not "fullmatch" name pattern.
            ValueError: if constant has been already added.
        """
        if not isinstance(constant, str):
            raise TypeError()
        if re.fullmatch(cls._name_pattern, constant) == None:
            raise ValueError(f"{constant} does not match name pattern.")
        if constant in cls._constant_set:
            return
        cls._constant_set.add(constant)

    @classmethod
    def get_parity(cls, predicate:str) -> int:
        if not isinstance(predicate, str):
            raise TypeError()
        if not predicate in cls._predicate_set:
            raise ValueError(f"unknown predicate {predicate}")
        return cls._arity_dict[predicate]

    @classmethod
    def is_observable(cls, predicate:str) -> bool:
        if not isinstance(predicate, str):
            raise TypeError()
        if not predicate in cls._predicate_set:
            raise ValueError(f"unknown predicate {predicate}")
        return cls._observability_dict[predicate]

    @classmethod
    def clear(cls) -> None:
        """Clear all class variables."""
        cls._constant_set.clear()
        cls._predicate_set.clear()
        cls._arity_dict.clear()
        cls._observability_dict.clear()
        cls._unique_table.clear()

    def __new__(cls, *args: str) -> "AtomicSentence":
        """Creates a new sentence only if no identical sentence exists.


        Args:
            args: A tuple of strings: a predicate and arguments for it.

        Returns:
            An AtomicSentence object.

        Raises:
            TypeError: if some argument is not a str.
            ValueError: if no argument.
            ValueError: if the 1st argument is an unknown predicate.
            ValueError: if the 2nd or later argument is an unknown constant.
            ValueError: if the number of arguments is invalid.
        """
        for x in args:
            if not isinstance(x, str):
                raise TypeError()
        if len(args) == 0:
            raise ValueError(f"no argument given")
        if not args[0] in cls._predicate_set:
            raise ValueError(f"unknown predicate: {args[0]}")
        for x in args[1:]:
            if not x in cls._constant_set:
                raise ValueError(f"unknown constant: {x}")
        if len(args) != cls._arity_dict[args[0]] + 1:
            raise ValueError(f"invalid number of arguments: {args}")
        key = cls._to_key(args)
        if key in cls._unique_table:
            return cls.unique_table[key]
        res = super().__new__(cls)
        cls._unique_table[key] = res
        res.data = args
        """A tuple of strings: a predicate and arguments for the predicate."""
        return res

    @staticmethod
    def _to_key(tup: Tuple[str]) -> str:
        return tup[0] + "(" + ",".join(tup[1:]) +  ")"

    def __str__(self) -> str:
        """Converts an atomic sentence to a string."""
        return type(self)._to_key(self.data)

    @classmethod
    def read(cls, s:str) -> "AtomicSentence":
        """Converts a string to an AtomicSentence object.

        Args:
            s: A string representation of an atomic sentence

        Returns:
            An AtomicSentence object.

        Raises:
            ValueError: if the format of a string is invalid.
        """
        s = s.strip()
        pos = s.find("(")
        if pos == -1:
            raise ValueError(f"no left parenthesis: {s}")
        args = []
        args.append(s[:pos].strip())
        if s[-1] != ")"
            raise ValueError(f"no ending right parenthesis: {s}")
        for x in s[pos+1:-1].split(","):
            args.append(x.strip())
        return cls(tuple(args))


Sentence = Union[str, AtomicSentence, Tuple["Sentence"]]
"""Sentence is a recursive type defined loosely for simplicity."""

class SentenceInterpreter:

    _op_name_set  = set()
    """Set of operator names."""
    _op_dict      = {}
    """Dictionary that maps operator name to operator."""
    _obj_dict     = {}
    """Dictionary that maps constant name to object in domain of discourse."""
    _prd_dict     = {}
    """Dictionary that maps predicate name to predicate."""
    _name_pattern: Final[str] = r"[a-zA-Z0-9_+-@&|*%/~^=]+"
    """Name pattern for operators."""

    @classmethod
    def set_constant_interpretation(cls, name: str, obj: Any) -> None:
        if name in cls._obj_dict:
            raise Exception(f"constant {name} ready set.")
        cls._obj_dict[name] = obj

    @classmethod
    def set_predicate_interpretation\
        (cls, name: str, prd: Callable[[List[Any]], Any]) -> None:
        if name in cls._prd_dict:
            raise Exception(f"predicate {name} already set.")
        cls._prd_dict[name] = prd

    @classmethod
    def set_operator_interpretation\
        (cls, name: str, op: Callable[[List[Any]], Any]) -> None:
        """Adds an operator.

        Args:
            name: An operator name.
            op: An operator

        Returns:
            None

        Raises:
            TypeError: if name is not a str.
            ValueError: if name is an empty string.
            ValueError: if name does not "fullmatch" [a-zA-Z0-9_+-@&|*%/~^=]+.
            ValueError: if name has been already added.
        """
        if not isinstance(name, str):
            raise TypeError()
        if name == "":
            raise ValueError(f"empty operator name.")
        if re.fullmatch(cls._name_pattern, name) == None:
            raise ValueError(f"unexpected character found: {name}")
        if name in cls._op_name_set:
            raise ValueError(f"operator {name} already set.")
        cls._op_name_set.add(name)
        cls._op_dict[name] = op

    @classmethod
    def clear(cls) -> None:
        """Clear all class variables."""
        cls._op_name_set.clear()
        cls._obj_dict.clear()
        cls._prd_dict.clear()
        cls._op_dict.clear()

    @classmethod
    def _interprete_atomic_sentence(cls, atom: Union[str, AtomicSentence],\
        world: Optional[int] = None) -> Any:
        """Interpretes an AtomicSentence object or its string representation."""
        if isinstance(atom, str):
            atom = AtomicSentence.read(atom)
        if not isinstance(atom, AtomicSentence):
            raise TypeError()
        name = atom[0]
        if not name in cls._prd_dict:
            raise ValueError(f"unknown predicate {name}")
        prd = cls._prd_dict[name]
        return prd(atom, world=world)

    @classmethod
    def interprete\
        (cls, sentence: Sentence, world: Optional[int] = None) -> Any:
        """Interpretes a sentence.

        Args:
            sentence: A Sentence object.
            world: A possible world at which truth values of unobservable atoms
            are interpreted.

        Returns:
            Any

        Raises:
            TypeError: if some element is none of str, AtomicSentence, and tuple.
            ValueError: if empty tuple is included.
            TypeError: if the first entry of a tuple is not a str.
            Exception: if unknown operator name is included.
        """
        def _interprete_rec(stc: Sentence, world: Optional[int]) -> Any:
            if isinstance(stc, str) or isinstance(stc, AtomicSentence):
                return cls._interprete_atomic_sentence(stc, world=world)
            if not isinstance(stc, tuple):
                raise TypeError()
            if len(stc) == 0:
                raise ValueError("empty tuple found")
            name = stc[0]
            if not isinstance(name, str):
                raise TypeError()
            if not name in cls._op_name_set:
                raise Exception(f"unknown operator {name}")
            op = cls._op_dict[name]
            return op([_interprete_rec(substc, world) for substc in stc[1:]])
        return _interprete_rec(sentence, world)
