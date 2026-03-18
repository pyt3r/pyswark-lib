import functools
import pydrive2.fs
from fsspec.implementations.local import LocalFileSystem

from pyswark.core.fsspec import fix


def path(func):

    @functools.wraps(func)
    def wrapper( self, path, *args, **kwargs ):

        handler = fix.getHandler( None, self.protocol, self.target_username )

        if handler:
            root = handler.getPath()
            if path and not path.startswith( str( root )):
                path = str( root / str( path ).lstrip( '/' ))

        return func( self, path, *args, **kwargs )

    return wrapper



class Base:
    protocol = None

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        #self.path = kwargs.get( 'path', None )
        self.target_username = kwargs.get( 'target_username', None )

    @path
    def open( self, path, *args, **kw ):
        return super().open( path, *args, **kw )


class GDriveFileSystem( Base, pydrive2.fs.GDriveFileSystem ):
    """GDrive filesystem registered under the ``gdrive2`` protocol.

    When used via ``fsspec.filesystem('gdrive2', target_username=...)``,
    the ``root`` attribute is set from the sekret's ``path``. This
    override makes relative paths passed to ``fs.open(...)`` behave
    like ``gdrive2://@user/<root-relative-path>``.
    """
    protocol = 'gdrive2'



class PyswarkFileSystem( Base, LocalFileSystem ):
    """Local filesystem rooted at the pyswark package directory.

    Paths are resolved relative to the installed ``pyswark`` package,
    e.g. ``data/df.csv`` → ``<pyswark_root>/data/df.csv``.
    """
    protocol = 'pyswark'
