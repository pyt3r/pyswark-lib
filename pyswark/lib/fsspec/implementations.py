import sys
import pydoc
from fsspec import AbstractFileSystem


class PythonFileSystem( AbstractFileSystem ):

    def open( self, path, *args, **kw ):
        exists, data = self.exists( path, returnDataToo=True, **kw )
        if not exists:
            raise ModuleNotFoundError( path )
        return self._open( path, data=data  )

    def _open( self, path, *args, **kw ):
        return PythonFile( path )

    def exists( self, path, returnDataToo=False, **kw ):
        with self._open( path ) as f:
            data = f.locate()
        result = True if data else False
        if returnDataToo:
            result = result, data
        return result


class PythonFile:

    def __init__( self, path, *args, data=None ):
        self.path = path
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        ...

    def close(self):
        ...

    def locate( self, reloadmodule=False, **kw ):
        if reloadmodule:
            return self._sys_pop_then_locate( **kw )
        else:
            return self._locate( **kw )

    def _sys_pop_then_locate( self, **kw ):
        parts = self.path.split('.')
        found, module = False, None
        if not found:
            found, module = self._sys_pop( parts )
        if not found:
            found, module = self._sys_pop( parts[:-1] )
        return self._locate( **kw )

    @staticmethod
    def _sys_pop( parts ):
        path = '.'.join( parts )
        found, module = False, None
        if path in sys.modules:
            return True, sys.modules.pop( path )
        return found, module

    def _locate( self, **kw ):
        if self.data:
            return self.data
        return pydoc.locate( self.path, **kw )
