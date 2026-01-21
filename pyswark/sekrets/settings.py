import pathlib
import pyswark
from pyswark.lib.aenum import AliasEnum


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
    _HIDDEN  = _PROJECT / 'iac-project' / 'hidden'

    SGDRIVE2      = ( 's-gdrive2', _HIDDEN / 's-gdrive2.json' )
    PRIVATE_CONDA = _HIDDEN / 'private-conda.docs.yaml'
    REDIS         = _HIDDEN / 'redis.docs.yaml'
    EXAMPLE_IAC   = ( 'example-iac', _HIDDEN / 'example-iac.json' )
