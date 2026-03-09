import functools

import pydrive2.fs

from pyswark.sekrets.api import get


def resolve_uri( uri ):
    """Parse a URI and return ``(protocol, full_path, sekret)`` when a
    username is present, otherwise ``None``.
    """
    from pyswark.core.models.uri.base import UriModel
    model  = UriModel( uri )
    scheme = model.scheme
    user   = model.username
    if scheme and user:
        sekret = get( user, scheme )
        root   = sekret.get( "path", "" )
        rel    = model.path.lstrip( "/" ) if model.path else ""
        full   = f"{ root }/{ rel }" if rel else root
        return scheme, full, sekret
    return None


def inject( fn ):
    """Resolve ``scheme://@username/path`` URIs and inject credentials."""
    @functools.wraps( fn )
    def wrapper( uri, *args, **kwargs ):
        resolved = resolve_uri( uri )
        if resolved:
            protocol, full_path, sekret = resolved
            return fn(
                full_path, *args,
                protocol=protocol, **{ **sekret, **kwargs },
            )
        return fn( uri, *args, **kwargs )
    return wrapper


def inject_target_username( fn ):
    """Resolve ``target_username`` kwarg and inject credentials."""
    @functools.wraps( fn )
    def wrapper( protocol, *, target_username=None, **kwargs ):
        if target_username:
            sekret = get( target_username, protocol )
            kwargs = { **sekret, **kwargs }
        return fn( protocol, **kwargs )
    return wrapper


class GDriveFileSystem( pydrive2.fs.GDriveFileSystem ):
    """GDrive filesystem registered under the ``gdrive2`` protocol."""
    protocol = "gdrive2"
