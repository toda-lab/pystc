# pystc: a simple but extensible Python module for sentences

import importlib.metadata

__version__ = importlib.metadata.version(__package__)

from .pystc import AtomicSentence, SentenceConverter

__all__ = [
    "AtomicSentence",
    "SentenceConverter",
]
