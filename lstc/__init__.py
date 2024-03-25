# lstc: Python module for extensible logical sentences

import importlib.metadata

__version__ = importlib.metadata.version(__package__)

from .lstc import AtomicSentence, SentenceInterpreter

__all__ = [
    "AtomicSentence",
    "SentenceInterpreter",
]
