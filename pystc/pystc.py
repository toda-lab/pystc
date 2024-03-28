from typing import Tuple, Union, Callable, Any, Optional, Final, List

import re

class AtomicSentence:
    """Sentences without any variables, logical connectives or quantifiers."""

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
    _name_pattern: Final[str] = r"[a-zA-Z0-9_+@&|*%/~^=!-]+"
    """Name patterns for constants and predicates."""

    @classmethod
    def add_predicate(cls,\
        name: str, arity: int, observable: bool = True) -> None:
        """Adds a predicate.

        Nothing is done if a predicate has already been added.

        Args:
            name: A predicate name.
            arity: The number of arguments a predicate has.
            observable: Whether it is an observable predicate or not.

        Returns:
            None

        Raises:
            TypeError:  if name is not a str.
            TypeError:  if arity is not an int.
            TypeError:  if observable is not a bool.
            ValueError: if name does not "fullmatch" name pattern.
            ValueError: if arity is negative.
        """
        if not isinstance(name, str):
            raise TypeError()
        if not isinstance(arity, int):
            raise TypeError()
        if not isinstance(observable, bool):
            raise TypeError()
        if re.fullmatch(cls._name_pattern, name) == None:
            raise ValueError(f"{name} does not match name pattern.")
        if arity < 0:
            raise ValueError(f"invalid arity: {arity}")
        if name in cls._predicate_set:
            return
        cls._predicate_set.add(name)
        cls._arity_dict[name] = arity
        cls._observability_dict[name] = observable

    @classmethod
    def add_constant(cls, name: str) -> None:
        """Adds a constant.

        Nothing is done if constant name has already been added.

        Args:
            name: A constant name.

        Returns:
            None

        Raises:
            TypeError:  if name is not a str.
            ValueError: if name does not "fullmatch" name pattern.
        """
        if not isinstance(name, str):
            raise TypeError()
        if re.fullmatch(cls._name_pattern, name) == None:
            raise ValueError(f"{name} does not match name pattern.")
        if name in cls._constant_set:
            return
        cls._constant_set.add(name)

    @classmethod
    def get_arity(cls, predicate_name:str) -> int:
        """Gets the number of arguments of a predicate.

        Args:
            predicate_name: A predicate name

        Returns:
            The number of arguments.

        Raises:
            TypeError: if predicate_name is not a str.
            ValueError: if unknown predicate.
        """
        if not isinstance(predicate_name, str):
            raise TypeError()
        if not predicate_name in cls._predicate_set:
            raise ValueError(f"unknown predicate {predicate_name}")
        return cls._arity_dict[predicate_name]

    @classmethod
    def is_observable(cls, predicate_name:str) -> bool:
        """Answers whether it is an observable predicate or not.

        Args:
            predicate_name: A predicate name

        Returns:
            True if observable predicate, and False otherwise.

        Raises:
            TypeError: if predicate_name is not a str.
            ValueError: if unknown predicate.
        """
        if not isinstance(predicate_name, str):
            raise TypeError()
        if not predicate_name in cls._predicate_set:
            raise ValueError(f"unknown predicate {predicate_name}")
        return cls._observability_dict[predicate_name]

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
            ValueError: if an unknown constant in the 2nd or later argument.
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
            return cls._unique_table[key]
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
        if s[-1] != ")":
            raise ValueError(f"no ending right parenthesis: {s}")
        for x in s[pos+1:-1].split(","):
            args.append(x.strip())
        return cls(*args)


Sentence = Union[str, AtomicSentence, Tuple["Sentence"]]

class SentenceConverter:
    """Provides functionality to convert sentences into something."""

    _con_name_set = set()
    """Set of connective names."""
    _con_dict     = {}
    """Dictionary that maps connective name to function."""
    _obj_dict     = {}
    """Dictionary that maps constant name to object in domain of discourse."""
    _prd_dict     = {}
    """Dictionary that maps predicate name to function."""
    _atom_type    = None
    """Type of an atomic sentece (AtomicSentence or a subclass of it)."""
    _name_pattern: Final[str] = r"[a-zA-Z0-9_+@&|*%/~^=!-]+"
    """Name pattern for connectives."""

    @classmethod
    def set_constant_destination(cls, name: str, obj: Any) -> None:
        """Sets a destination of a constant to be converted.

        Args:
            name: A constant name.
            obj: an object in domain of discourse.

        Returns:
            None

        Raises:
            TypeError:  if name is not a str.
            ValueError: if name has already been set.
        """
        if not isinstance(name, str):
            raise TypeError()
        if name in cls._obj_dict:
            raise ValueError(f"constant {name} ready set.")
        cls._obj_dict[name] = obj

    @classmethod
    def set_predicate_destination\
        (cls, name: str, func: Callable[[List[Any],int], Any]) -> None:
        """Sets a destination of a predicate to be converted.

        Args:
            name: A predicate name.
            func: A function to which a predicate is converted.

        Returns:
            None

        Raises:
            TypeError:  if name is not a str.
            ValueError: if name has already been set.
        """
        if not isinstance(name, str):
            raise TypeError()
        if name in cls._prd_dict:
            raise ValueError(f"predicate {name} already set.")
        cls._prd_dict[name] = func 

    @classmethod
    def set_connective_destination\
        (cls, name: str, func: Callable[[List[Any],int], Any]) -> None:
        """Adds a destination of a connective to be converted.

        Args:
            name: A connective name.
            func: A function to which a connective is converted.

        Returns:
            None

        Raises:
            TypeError:  if name is not a str.
            ValueError: if name does not name pattern.
            ValueError: if name has already been added.
        """
        if not isinstance(name, str):
            raise TypeError()
        if re.fullmatch(cls._name_pattern, name) == None:
            raise ValueError(f"{name} does not match name pattern.")
        if name in cls._con_name_set:
            raise ValueError(f"connective {name} already set.")
        cls._con_name_set.add(name)
        cls._con_dict[name] = func 

    @classmethod
    def set_atom_type(cls, atom_type: type) -> None:
        """Sets the type of an atom that constitutes a sentence.

        Args:
            atom_type: An atom type, an AtomicSentence or a subclass of it.

        Returns:
            None

        Raises:
            TypeError: if atom_type is not a type.
            Exception: if atom_type is not a subclass of AtomicSentence.
        """
        if not isinstance(atom_type, type):
            raise TypeError()
        if not issubclass(atom_type, AtomicSentence):
            raise Exception(f"invalid atom type: {atom_type}")
        cls._atom_type = atom_type

    @classmethod
    def clear(cls) -> None:
        """Clear all class variables."""
        cls._con_name_set.clear()
        cls._obj_dict.clear()
        cls._prd_dict.clear()
        cls._con_dict.clear()
        cls._atom_type = None

    @classmethod
    def _convert_atomic_sentence\
        (cls, atom: Union[str, AtomicSentence], world: Optional[int] = None)\
        -> Any:
        """Converts an AtomicSentence object or its string representation.

        Args:
            atom: An Atomic sentence object or its string representation.
            world: A possible world

        Returns:
            Any

        Raises:
            TypeError:  if atom is not a cls._atom_type.
            ValueError: if unknown predicate.
            Exception:  if _atom_type is not set.
        """
        if cls._atom_type is None:
            raise Exception("_atom_type is not set.")
        if isinstance(atom, str):
            atom = cls._atom_type.read(atom)
        if type(atom) != cls._atom_type:
            raise TypeError()
        name = atom.data[0]
        if not name in cls._prd_dict:
            raise ValueError(f"unknown predicate {name}")
        if type(atom).get_arity(name) != len(atom.data[1:]):
            raise ValueError(f"invalid number of arguments")
        func = cls._prd_dict[name]
        return func([cls._obj_dict[arg] for arg in atom.data[1:]], world)

    @classmethod
    def convert\
        (cls, sentence: Sentence, world: Optional[int] = None) -> Any:
        """Converts a sentence.

        Args:
            sentence: A sentence.
            world: A possible world

        Returns:
            Any

        Raises:
            TypeError:  if some element is none of str, cls._atom_type, and tuple.
            ValueError: if empty tuple is included.
            TypeError:  if the first entry of a tuple is not a str.
            Exception:  if unknown connective name is included.
            Exception:  if atom_type is not set.
        """
        def _convert_rec(stc: Sentence, w: Optional[int]) -> Any:
            if isinstance(stc, str) or type(stc) == cls._atom_type:
                return cls._convert_atomic_sentence(stc, world=w)
            if not isinstance(stc, tuple):
                raise TypeError()
            if len(stc) == 0:
                raise ValueError("empty tuple found")
            name = stc[0].strip()
            if not isinstance(name, str):
                raise TypeError()
            if not name in cls._con_name_set:
                raise Exception(f"unknown connective {name}")
            func = cls._con_dict[name]
            return func([_convert_rec(x, w) for x in stc[1:]], w)

        if cls._atom_type is None:
            raise Exception("_atom_type is not set.")
        return _convert_rec(sentence, world)
