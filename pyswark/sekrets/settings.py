import pathlib
import pyswark
from pyswark.lib.aenum import AliasEnum, Alias


class Mixin:

    @property
    def uri(self):
        uri = self.value
        if isinstance( uri, tuple ):
            uri = uri[1]
        if isinstance( uri, pathlib.Path ):
            uri = uri.as_posix()
        return uri


class Base( Mixin, AliasEnum ):
    pass


class Settings( Base ):
    _ROOT    = pathlib.Path( pyswark.__file__ ).parent
    _PROJECT = _ROOT / '..' / '..'
    _SEKRETS = _PROJECT / 'iac-project' / 'sekrets'

    GITHUB_IO_DEMO = './github-io-demo.gluedb', Alias( 'github-io-demo' )
    GDRIVE2        = _SEKRETS / 'gdrive2.gluedb', Alias( 'gdrive2' )
