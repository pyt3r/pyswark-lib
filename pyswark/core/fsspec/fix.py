"""fsspec fix – credential injection for scheme://@username/path URIs.

Resolves URIs of the form ``scheme://@username/path`` via :mod:`pyswark.sekrets`,
injects credentials and protocol into fsspec.open / fsspec.filesystem calls,
and provides a :class:`Handler` registry for protocol-specific behaviour.
"""
import functools
from pathlib import Path
from typing import ClassVar, Optional
from pydantic import Field, field_validator, model_validator
from pyswark.lib.pydantic import base

import pyswark.sekrets.api as sekrets_api
import pyswark.core.io.api as io_api

from pyswark.core.models.uri.base import UriModel
import pyswark


IMPLEMENTATIONS = {
    # Use pyswark's wrapped GDriveFileSystem so that paths opened via
    # fsspec.filesystem('gdrive2', ...) go through our subclass, which
    # can normalise paths relative to the sekret root.
    'gdrive2': 'pyswark.core.fsspec.implementations.GDriveFileSystem',
    'pyswark': 'pyswark.core.fsspec.implementations.PyswarkFileSystem',
}


def open( fn ):
    """Decorator that resolves ``scheme://@username/path`` URIs for fsspec.open.

    When the first argument is a URI with a username (e.g. ``gdrive2://@phb2114/file.json``),
    the URI is parsed, credentials are loaded from :mod:`pyswark.sekrets`, and the wrapped
    function is called with:

    - First argument: the resolved path (sekret root + URI path).
    - ``protocol``: the scheme (e.g. ``"gdrive2"``).
    - Remaining kwargs: the sekret mapping (credentials) merged with any caller kwargs.

    Non-matching URIs are passed through unchanged to the wrapped function.
    """
    @functools.wraps( fn )
    def wrapper( uri, *args, **kwargs ):
        handler  = getHandler( uri, **kwargs )

        if handler:
            uri             = handler.getPath()
            protocol        = handler.scheme
            target_username = handler.username
            sekret          = handler.getSekret()
            
            kwargs = { 
                'protocol' : protocol,
                'target_username': target_username,
                **sekret,
                **kwargs,
            }

        return fn( uri, *args, **kwargs )

    return wrapper


def filesystem( fn ):
    """Decorator that injects credentials for fsspec.filesystem when ``target_username`` is set.

    If the wrapped function is called with ``target_username=...``, credentials for that
    user and the given protocol are loaded from :mod:`pyswark.sekrets` and merged into
    the keyword arguments passed to the underlying filesystem implementation.
    """
    @functools.wraps( fn )
    def wrapper( protocol, *, target_username=None, **kwargs ):
        handler  = getHandler( scheme=protocol, username=target_username )
        if handler:
            protocol = handler.scheme
            sekret   = handler.getSekret()
            kwargs = { 
                **sekret,
                **kwargs,
            }

        return fn( protocol, target_username=target_username, **kwargs, )

    return wrapper


def getHandler( uri=None, scheme=None, username=None, **kw ):
    """Return a protocol-specific :class:`Handler` for the given URI, scheme, or username.

    At least one of *uri*, *scheme*, or *username* must be provided.
    """
    return Handler.getHandler( uri=uri, scheme=scheme, username=username )


class Handler( base.BaseModel ):
    """Base handler for resolving URIs and credentials per protocol.

    Subclasses are registered in :attr:`HANDLERS` by scheme; :meth:`getHandler` returns
    the appropriate subclass (e.g. :class:`Gdrive2`) when the URI or scheme matches.
    """
    HANDLERS : ClassVar[dict[str, str]] = {
        'gdrive2': 'pyswark.core.fsspec.fix.Gdrive2',
        'pyswark': 'pyswark.core.fsspec.fix.Pyswark',
    }
    uri      : Optional[UriModel] = Field( default=None )
    scheme   : Optional[str] = Field( default=None )
    username : Optional[str] = Field( default=None )

    @classmethod
    def getHandler(cls, uri=None, scheme=None, username=None, **kw):
        """Build a handler instance for the given *uri*, *scheme*, or *username*.

        If *uri* is provided, scheme and username are inferred from it. Returns a
        protocol-specific subclass (e.g. :class:`Gdrive2`) when the scheme is in
        :attr:`HANDLERS`, otherwise returns a base :class:`Handler`.
        """
        if not any( [ uri, scheme, username ] ):
            raise ValueError( 'at least one of uri, scheme, or username must be provided' )

        handler = cls( uri=uri, scheme=scheme, username=username, **kw )
        scheme = handler.scheme

        if scheme in cls.HANDLERS:
            path = cls.HANDLERS[ scheme ]
            Handler = io_api.read( path, datahandler='python' )
            handler = Handler( uri=handler.uri, scheme=handler.scheme, username=handler.username )
            return handler

    def __init__(self, uri=None, scheme=None, username=None, **kw):
        super().__init__( uri=uri, scheme=scheme, username=username )

    @field_validator( 'uri', mode='before' )
    def _uri(cls, uri):
        if uri:
            return uri if isinstance( uri, UriModel ) else UriModel( uri )

    @model_validator( mode='after' )
    def _others(self):
        if self.uri and not self.scheme:
            self.scheme = self.uri.scheme
        
        if self.uri and not self.username:
            self.username = self.uri.username
        
        self.scheme   = ( self.scheme or '' ).lower()
        self.username = ( self.username or '' ).lower()
        return self

    def getSekret( self ):
        """Return the credential dict to pass to the filesystem; subclasses may filter keys."""
        return {}

    def _getSekret( self ):
        """Return the full credential mapping from :mod:`pyswark.sekrets` for this handler."""
        return sekrets_api.get( self.username, self.scheme )

    def getPath(self):
        """Return the path component of the URI as a :class:`pathlib.Path`."""
        return Path( self.uri.path if self.uri else '' )


class Gdrive2( Handler ):
    """Handler for ``gdrive2://@username/path`` URIs; resolves path relative to sekret root."""

    def getSekret(self):
        """Return credentials for GDrive, including the root ``path`` key required by the FS."""
        return self._getSekret()

    def getPath(self):
        """Return the full path: sekret root path joined with the URI path (leading slash stripped)."""
        root = Path( self._getSekret().get( 'path', '' ) )
        path = str( super().getPath() )
        return root / path.lstrip('/')


class Pyswark( Handler ):
    """Handler for ``pyswark://path`` URIs; resolves path relative to the pyswark package root."""

    def getPath(self):
        """Return the relative path (leading slash stripped) for the PyswarkFileSystem."""
        root = Path( pyswark.__file__ ).parent
        path = str( super().getPath() )
        return root / path.lstrip('/')