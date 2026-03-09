"""
Filesystem Abstraction
======================

This module provides a unified filesystem interface built on fsspec,
with additional protocol support (e.g., ``python://`` for Python objects).

Functions
---------
open(uri)
    Open a file from any supported URI.
filesystem(protocol)
    Get a filesystem instance for a protocol.
"""

import fsspec

IMPLEMENTATIONS = {
    'python' : "pyswark.lib.fsspec.implementations.PythonFileSystem",
    'gdrive2': "pydrive2.fs.GDriveFileSystem",
}
[ fsspec.register_implementation( *i ) for i in IMPLEMENTATIONS.items() ]


def open( uri, *args, **kwargs ):
    """
    Open a file from any supported URI.

    Wraps fsspec.open with additional protocol support.

    Parameters
    ----------
    uri : str
        The URI to open.
    *args
        Additional positional arguments passed to fsspec.
    **kwargs
        Additional keyword arguments passed to fsspec.

    Returns
    -------
    OpenFile
        A file-like object.
    """
    return fsspec.open( uri, *args, **kwargs )


def filesystem( protocol, **kwargs ):
    """
    Get a filesystem instance for a protocol.

    Parameters
    ----------
    protocol : str
        The protocol name (e.g., 'file', 'python', 's3').
    **kwargs
        Additional arguments passed to the filesystem.

    Returns
    -------
    AbstractFileSystem
        A filesystem instance.
    """
    return fsspec.filesystem( protocol, **kwargs )
