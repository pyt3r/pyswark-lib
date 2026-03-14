import pathlib
from typing import ClassVar
from pydantic import Field

import pyswark
from pyswark.core.models.uri import interface, ext


class Inputs( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = 'pyswark'


class Model( interface.Model ):
    inputs  : Inputs
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = Inputs.SCHEME

    @property
    def fsspec(self):
        return self.path

    @property
    def Ext(self):
        if self.Path:
            return ext.Ext( name=self.Path.name )
