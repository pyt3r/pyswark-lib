import re
import os
import pathlib
from typing import ClassVar, Union
from pydantic import Field, field_validator

from pyswark.core.models import xputs, function
from pyswark.core.models.uri import ext

class Inputs( xputs.BaseInputs ):
    uri    : str
    SCHEME : ClassVar = ''


class Outputs( xputs.BaseOutputs ):
    scheme   : Union[ str, None ]
    username : Union[ str, None ]
    password : Union[ str, None ]
    host     : Union[ str, None ]
    port     : Union[ str, None ]
    path     : Union[ str, None ]
    query    : Union[ str, None ]
    fragment : Union[ str, None ]


class Model( function.FunctionModel ):
    inputs  : Inputs
    outputs : Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = Inputs.SCHEME

    PATTERN: ClassVar = re.compile(
        r'^(?:(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*)://)?'
        r'(?:(?P<username>[^:@\s]+)'
        r'(?::(?P<password>[^@\s]*))?@)?'
        r'(?P<host>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|localhost|\d{1,3}(?:\.\d{1,3}){3})?'
        r'(?::(?P<port>\d+))?'
        r'(?P<path>/[^?#]*)?'
        r'(?:\?(?P<query>[^\s#]*))?'
        r'(?:#(?P<fragment>[^\s]*))?$',
        re.IGNORECASE
    )

    @classmethod
    def function( cls, inputs ):
        match = cls.PATTERN.match( inputs.uri )

        if not match:
            raise ValueError( f"cannot match { inputs.uri= } to the uri regex pattern" )

        return Outputs( **match.groupdict() )

    @property
    def scheme(self):
        return self._getProperty( 'scheme' )

    @property
    def username(self):
        return self._getProperty( 'username' )

    @property
    def password(self):
        return self._getProperty( 'password' )

    @property
    def host(self):
        return self._getProperty( 'host' )

    @property
    def port(self):
        return self._getProperty( 'port' )

    @property
    def Path(self):
        path = self._getProperty( 'path' )
        if path:
            return pathlib.Path( path ) # cleans up duplicate slashes, i.e. ///path/to///file//

    @property
    def path(self):
        return str( self.Path )

    @property
    def query(self):
        return self._getProperty( 'query' )

    @property
    def fragment(self):
        return self._getProperty( 'fragment' )

    def _getProperty( self, name ):
        model = self.getModel()
        return getattr( model.outputs, name )

    def getModel(self):
        return self._getModel( self.inputs.uri )

    @classmethod
    def _getModel( cls, uri ):
        return cls( uri )

    @property
    def Ext(self):
        return self._getProperty( 'Ext' )
        
    @property
    def fsspec(self):
        """
        Define representation for fsspec:
         - scheme://username:password@domain.com:8080/my path/to/a page?query=value#section
        """
        return self._getProperty( 'fsspec' )


class InputsWithUriPatch( Inputs ):
    uri    : str
    SCHEME : ClassVar = ''

    @field_validator( 'uri' )
    def uriPatch( cls, uri ):
        """ allows for schemes with less slashes, i.e. scheme:/path/to/file """
        return cls.patch( uri, cls.SCHEME )

    @staticmethod
    def patch( uri, scheme ):
        prefix = f'{ scheme }:'
        if uri.startswith( prefix ):
            path    = pathlib.Path( f'{ os.sep }{ uri[ len(prefix): ]}' )
            slashes = '/'*2 if os.sep == '/' else '/'*3
            uri     = f'{ prefix }{ slashes }{ path }'
        return uri