from typing import ClassVar
from pydantic import Field

from pyswark.core.models.uri import interface, ext


class InputsHttp( interface.Inputs ):
    uri    : str
    SCHEME : ClassVar = 'http'

class InputsHttps( interface.Inputs ):
    uri    : str
    SCHEME : ClassVar = 'https'


class ModelHttp( interface.Model ):
    inputs  : InputsHttp
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = InputsHttp.SCHEME

    @property
    def scheme(self):
        return self.SCHEME

    @property
    def Ext(self):
        return ext.Ext( self.host )

    @property
    def fsspec(self):
        uri    = self.inputs.uri
        prefix = f'{ self.SCHEME }:'
        return uri if uri.startswith( prefix ) else f'{ prefix }//{ uri }'


class ModelHttps( ModelHttp ):
    inputs  : InputsHttps
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = InputsHttps.SCHEME


class ModelGuess( interface.Model ):
    inputs  : interface.Inputs
    outputs : interface.Outputs = Field( default=None, description="" )

    def __new__( cls, uri ):
        """ detect if the uri contains a relative or absolute path """

        if uri.startswith('www.'):
            return ModelHttps( f'https://{ uri }' )

        if uri.startswith('https:'):
            return ModelHttps( uri )

        if uri.startswith('http:'):
            return ModelHttp( uri )

        return ModelHttps( uri )
