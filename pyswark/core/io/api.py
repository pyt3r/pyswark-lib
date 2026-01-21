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
>>>
>>> # Control logging verbosity (can be set/unset at runtime)
>>> io.set_verbosity('WARNING')  # Suppress INFO messages
>>> io.set_verbosity('INFO')    # Show I/O operations (default)
>>> 
>>> # Temporarily change verbosity for specific operations
>>> with io.verbosity('INFO'):
...     df = io.read('file:./important.csv')  # Shows logging
>>> # Verbosity automatically restored
"""

from pyswark.core.io.iohandler import IoHandler
from pyswark.core.io import guess as _guess
from pyswark.util.log import (
    set_verbosity as _set_verbosity,
    get_verbosity as _get_verbosity,
    verbosity as _verbosity,
)


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


def set_verbosity( level ):
    """
    Set the verbosity level for I/O logging operations.
    
    Controls when logging information is sent to the console. By default,
    all I/O operations log at INFO level, which includes messages like
    "Reading uri='...'..." and "done.".
    
    This can be called multiple times at runtime to change the verbosity
    level. The change takes effect immediately.
    
    Parameters
    ----------
    level : str or int
        Logging level. Can be one of:
        - 'DEBUG' or logging.DEBUG (10) - Most verbose, shows all messages
        - 'INFO' or logging.INFO (20) - Default, shows I/O operations
        - 'WARNING' or logging.WARNING (30) - Only warnings and errors
        - 'ERROR' or logging.ERROR (40) - Only errors
        - 'CRITICAL' or logging.CRITICAL (50) - Only critical errors
        
        Can also be a string like 'debug', 'info', 'warning', 'error', 'critical'
        (case-insensitive).
    
    Examples
    --------
    >>> from pyswark.core.io import api as io
    >>> 
    >>> # Suppress I/O logging messages
    >>> io.set_verbosity('WARNING')
    >>> df = io.read('file:./data.csv')  # No logging output
    >>> 
    >>> # Show all messages
    >>> io.set_verbosity('DEBUG')
    >>> 
    >>> # Restore default
    >>> io.set_verbosity('INFO')
    >>> 
    >>> # Use logging constants
    >>> import logging
    >>> io.set_verbosity(logging.ERROR)
    """
    return _set_verbosity( level )


def get_verbosity():
    """
    Get the current verbosity level.
    
    Returns
    -------
    int
        The current logging level (e.g., logging.INFO, logging.WARNING).
    
    Examples
    --------
    >>> from pyswark.core.io import api as io
    >>> import logging
    >>> level = io.get_verbosity()
    >>> level == logging.INFO
    True
    """
    return _get_verbosity()


def verbosity( level ):
    """
    Context manager for temporarily setting verbosity level.
    
    The verbosity level is changed for the duration of the context
    and automatically restored when exiting. This is useful for
    selectively enabling logging for specific operations.
    
    Parameters
    ----------
    level : str or int
        Logging level to use temporarily. See set_verbosity() for details.
    
    Examples
    --------
    >>> from pyswark.core.io import api as io
    >>> 
    >>> # Most operations are quiet
    >>> io.set_verbosity('WARNING')
    >>> 
    >>> with io.verbosity('INFO'):
    ...     df = io.read('file:./important.csv')  # Shows logging
    ... 
    >>> # Verbosity automatically restored to WARNING
    >>> df2 = io.read('file:./other.csv')  # No logging
    >>> 
    >>> # Or suppress logging for specific operations
    >>> io.set_verbosity('INFO')
    >>> with io.verbosity('WARNING'):
    ...     df3 = io.read('file:./quiet.csv')  # No logging
    ... 
    >>> # Verbosity restored to INFO
    """
    return _verbosity( level )