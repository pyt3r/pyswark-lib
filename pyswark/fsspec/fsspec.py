"""
pyswark.fsspec
==============

Unified filesystem interface with automatic credential injection.

Wraps :mod:`fsspec` so that URIs containing a ``username`` component
automatically resolve credentials via :mod:`pyswark.sekrets`.

URI format
----------
``scheme://@username/path``

* **scheme**   - the fsspec protocol name (e.g. ``gdrive2``)
* **username** - the credential identifier stored in pyswark.sekrets
* **path**     - path relative to the credential's root

Standard fsspec URIs (``protocol://...``, local paths, etc.) are passed
through unchanged.

Quick start
-----------
>>> from pyswark import fsspec
>>>
>>> # Open a file on GDrive (credentials resolved automatically)
>>> with fsspec.open("gdrive2://@phb2114/phb2114-keepme.json") as f:
...     data = f.read()
>>>
>>> # Walk a remote directory
>>> for root, dirs, files in fsspec.walk("gdrive2://@phb2114/PUBLIC"):
...     print(root, dirs, files)
>>>
>>> # Get a filesystem instance directly
>>> fs = fsspec.filesystem("gdrive2", target_username="phb2114")
"""

import fsspec as _fsspec
from pyswark.fsspec import fix


IMPLEMENTATIONS = {
    **fix.IMPLEMENTATIONS,
    "pyswark": "pyswark.fsspec.implementations.PyswarkFileSystem",
}
[ _fsspec.register_implementation( *i ) for i in IMPLEMENTATIONS.items() ]


@fix.open
def open( uri, *args, **kwargs ):
    """Open a file, injecting credentials when the URI contains a username."""
    return _fsspec.open( uri, *args, **kwargs )


@fix.filesystem
def filesystem( protocol, **kwargs ):
    """Get a filesystem instance, optionally injecting credentials
    via *target_username*."""
    return _fsspec.filesystem( protocol, **kwargs )
