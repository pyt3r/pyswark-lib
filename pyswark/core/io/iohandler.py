from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator, model_validator

from pyswark.core import extractor
from pyswark.core.io import guess
from pyswark.core.io.datahandler import DataHandler


class IoHandler( extractor.Extractor ):
    uri         : str
    datahandler : Optional[ str ] = ""
    kw          : Optional[ dict ] = Field( default_factory=lambda: {} )

    @field_validator( 'uri', mode='before' )
    def _uri( cls, uri ):
        if isinstance( uri, Path ):
            return str( uri )
        return uri

    @field_validator( 'datahandler', mode='before' )
    def _datahandler( cls, datahandler ):
        if isinstance( datahandler, DataHandler ):
            return datahandler.name
        return datahandler

    @model_validator( mode='after' )
    def _validate(self):
        if self.uri.startswith( "python:" ):
            alreadySet = self.kw and 'reloadmodule' in self.kw
            if not alreadySet:
                self.kw.update({ "reloadmodule": True })
        return self

    def extract( self ):
        return self.read()

    def read( self ):
        handler = self.acquire()
        return handler.read( **self.kw )

    def acquire( self ):
        uri         = self.uri
        datahandler = self.datahandler

        if not datahandler:
            klass = self.guess()
        else:
            klass = DataHandler.get( datahandler )
        return klass( uri )

    def write( self, data, **kwargs ):
        handler = self.acquire()
        return handler.write( data, **{ **self.kw, **kwargs } )

    def guess( self ):
        return guess.api( self.uri )


