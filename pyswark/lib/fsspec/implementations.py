import pydoc
from fsspec import AbstractFileSystem


class PythonFileSystem( AbstractFileSystem ):

    def open( self, path, *args, **kwargs ):
        exists, data = self.exists( path, returnDataToo=True )
        if not exists:
            raise ModuleNotFoundError( path )
        return self._open( path, data=data )

    def _open( self, path, *args, **kwargs ):
        return PythonFile( path )

    def exists( self, path, returnDataToo=False ):
        with self._open( path ) as f:
            data = f.locate()
        result = True if data else False
        if returnDataToo:
            result = result, data
        return result


class PythonFile:

    def __init__(self, path, *args, data=None):
        self.path = path
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        ...

    def close(self):
        ...

    def locate(self):
        if self.data:
            return self.data
        return pydoc.locate( self.path )