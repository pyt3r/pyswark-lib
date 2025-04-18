import os
import pathlib
from typing import ClassVar
from pydantic import Field


from pyswark.core.models.uri import interface


class InputsRelative( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = 'file-relative'

class InputsAbsolute( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = 'file-absolute'

class Inputs( interface.Inputs ):
    uri    : str
    SCHEME : ClassVar = 'file'


class ModelRelative( interface.Model ):
    inputs  : InputsRelative
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = InputsRelative.SCHEME

    @property
    def Path(self):
        path = str( super().Path )
        if path.startswith( os.sep ):
            return pathlib.Path( path[len(os.sep):] )
        return path

class ModelAbsolute( interface.Model ):
    inputs  : InputsAbsolute
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = InputsAbsolute.SCHEME

    @property
    def Path(self):
        Path = super().Path
        return Path

class Model( interface.Model ):
    inputs  : Inputs
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = Inputs.SCHEME

    def __new__( cls, uri ):
        """ detect if the uri contains a relative or absolute path """
        prefix = f'{ cls.SCHEME }:'

        klass = ModelRelative
        if uri.startswith(( f'{ prefix }/', f'{ prefix }{ os.sep }' )):
            klass = ModelAbsolute

        return klass( f'{ klass.SCHEME }:{ uri[len(prefix):] }' )
