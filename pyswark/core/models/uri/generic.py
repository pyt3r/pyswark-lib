from pydantic import Field

from pyswark.core.models.uri import interface, ext


class Model( interface.Model ):
    inputs  : interface.Inputs
    outputs : interface.Outputs = Field( default=None, description="" )

    @property
    def fsspec(self):
        return self.inputs.uri

    @property
    def Ext(self):
        if self.Path:
            return ext.Ext( name=self.Path.name )