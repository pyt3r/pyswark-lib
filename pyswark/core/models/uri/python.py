import os
from typing import ClassVar
from pydantic import Field

from pyswark.core.models.uri import interface, ext


class Inputs( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = 'python'


class Model( interface.Model ):
    inputs  : Inputs
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = Inputs.SCHEME

    @property
    def path(self):
        path = super().path
        while path.startswith(( '/', os.sep )):
            path = path[1:]
        return path

    @property
    def fsspec(self):
        return f'{ self.scheme }://{ self.path }'

    @property
    def Ext(self):
        return ext.Ext( '' )

