import pyswark.lib.fsspec as fsspec
from pyswark.core.models.uri.base import UriModel
from pyswark.core.datahandler import decorate


class Log(decorate.Log):

    PAYLOAD = {
        "r"  : "Reading",
        "w"  : "Writing",
        "rm" : "Removing"
    }


class AbstractDataHandler:
    MODE_R = 'r'
    MODE_W = 'w'

    def __init__( self, uri ):
        self.uri = UriModel( uri )

    @property
    def path(self):
        return self.uri.path

    def exists(self):
        return self.fs.exists( self.path )

    def open( self, *args, **kwargs ):
        return fsspec.open( self.uri.fsspec, *args, **kwargs )

    @Log.decorate('r')
    def read( self, **kwargs ):
        with self.open( self.MODE_R ) as fp:
            result = self._read( fp, **kwargs )
        return result

    @Log.decorate('w')
    def write( self, data, overwrite=False, **kwargs ):
        if not overwrite and self.exists():
            raise CannotOverwrite( self.uri )

        if overwrite and self.exists():
            self.rm()

        with self.open( self.MODE_W ) as fp:
            self._write( data, fp, **kwargs )

    def _read( self, fp, **kwargs ):
        raise NotImplementedError

    def _write( self, data, fp, **kwargs ):
        raise NotImplementedError

    @Log.decorate('rm')
    def rm(self):
        return self.fs.rm( self.path )

    @property
    def fs(self):
        return self.open().fs


class CannotOverwrite( Exception ):
    pass