"""
Unified I/O API
================

This module provides a unified interface for reading and writing data
from any URI scheme. It abstracts away the details of different data
sources (files, URLs, Python objects) behind a consistent API.

Supported URI Schemes
---------------------
- ``file:`` - Local filesystem (e.g., ``file:./data.csv``)
- ``pyswark:`` - Package data files (e.g., ``pyswark:/data/ohlc-jpm.csv.gz``)
- ``python:`` - Python objects by import path (e.g., ``python://mymodule.MyClass``)
- ``http:``/``https:`` - Remote URLs

Example
-------
>>> from pyswark.core.io import api as io
>>>
>>> # Read from various sources
>>> df = io.read('pyswark:/data/ohlc-jpm.csv.gz')
>>> config = io.read('file:./config.yaml')
>>>
>>> # Write data
>>> io.write(df, 'file:./output.csv')
"""

from pyswark.core.io.iohandler import IoHandler
from pyswark.core.io import guess as _guess


def read( uri, datahandler=None, **kw ):
    """
    Read data from any supported URI.

    This is the primary entry point for loading data in pyswark. The
    function automatically determines the appropriate handler based on
    the URI scheme and file extension.

    Parameters
    ----------
    uri : str
        The URI to read from. Supports multiple schemes:
        
        - ``file:./path/to/file.csv`` - Local file
        - ``pyswark:/data/filename`` - Package data
        - ``python://module.Class`` - Python object
        - ``https://example.com/data.json`` - Remote URL
        
    datahandler : str, optional
        Override the automatic datahandler selection.
    **kw
        Additional keyword arguments passed to the underlying reader
        (e.g., ``index_col=0`` for pandas).

    Returns
    -------
    Any
        The loaded data (type depends on the file format).

    Example
    -------
    >>> df = read('pyswark:/data/ohlc-jpm.csv.gz')
    >>> config = read('file:./config.yaml')
    """
    contents = IoHandler( uri=uri, datahandler=datahandler, kw=kw )
    return contents.read()


def write( data, uri, datahandler=None, **kw ):
    """
    Write data to any supported URI.

    Parameters
    ----------
    data : Any
        The data to write.
    uri : str
        The destination URI. Supports ``file:`` scheme for local files.
    datahandler : str, optional
        Override the automatic datahandler selection.
    **kw
        Additional keyword arguments passed to the underlying writer.

    Returns
    -------
    Any
        Result from the write operation (typically None or the path).

    Example
    -------
    >>> write(df, 'file:./output.csv', index=False)
    >>> write(config, 'file:./config.yaml')
    """
    contents = IoHandler( uri=uri, datahandler=datahandler, kw=kw )
    return contents.write( data )


def acquire( uri, datahandler=None ):
    """
    Acquire a file handle or connection for a URI without reading.

    Useful for streaming or when you need direct access to the
    underlying resource.

    Parameters
    ----------
    uri : str
        The URI to acquire.
    datahandler : str, optional
        Override the automatic datahandler selection.

    Returns
    -------
    Any
        A file-like object or connection handle.
    """
    contents = IoHandler( uri=uri, datahandler=datahandler )
    return contents.acquire()


def isUri( uri ):
    """
    Check if a string is a valid pyswark URI.

    Parameters
    ----------
    uri : str
        The string to validate.

    Returns
    -------
    bool
        True if the string is a recognized URI scheme, False otherwise.

    Example
    -------
    >>> isUri('file:./data.csv')
    True
    >>> isUri('/plain/path/data.csv')
    False
    """
    try:
        guess( uri )
        return True
    except ValueError:
        return False

def guess( uri ):
    return _guess.api( uri )