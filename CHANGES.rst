.. _`changes`

CHANGES
=======

Version 2.0.0 - 2024-3-29
--------------------------

Changed
^^^^^^^

- Changed ``SentenceConverter`` so that the type of an atomic sentence can be specified by ``set_atom_type()``.
- Made it mandatory to call ``set_atom_type()`` as well as other set methods: otherwise, an exception will be raised.
