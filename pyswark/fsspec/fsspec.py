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
import pyswark.lib.fsspec as _pyswark_fsspec
from pyswark.fsspec.implementations import (
    inject,
    inject_target_username,
    resolve_uri,
)


__all__ = ["open", "filesystem", "walk"]


IMPLEMENTATIONS = {
    **_pyswark_fsspec.IMPLEMENTATIONS,
    "gdrive2": "pyswark.fsspec.implementations.GDriveFileSystem",
}
[ _fsspec.register_implementation( *i ) for i in IMPLEMENTATIONS.items() ]


@inject
def open( uri, *args, **kwargs ):
    """Open a file, injecting credentials when the URI contains a username."""
    return _fsspec.open( uri, *args, **kwargs )


@inject_target_username
def filesystem( protocol, **kwargs ):
    """Get a filesystem instance, optionally injecting credentials
    via *target_username*."""
    return _fsspec.filesystem( protocol, **kwargs )


def walk( uri, *args, **kwargs ):
    """Walk a remote directory, injecting credentials when the URI
    contains a username.

    Yields ``(root, dirs, files)`` tuples, just like :func:`os.walk`.
    """
    resolved = resolve_uri( uri )
    if resolved:
        protocol, full_path, sekret = resolved
        fs = _fsspec.filesystem( protocol, **{ **sekret, **kwargs } )
        return fs.walk( full_path, *args )

    return _fsspec.filesystem( "file" ).walk( uri, *args, **kwargs )
