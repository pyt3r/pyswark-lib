from typing import Optional
from pydantic import Field

from pyswark.core.io import iohandler


class IoModel( iohandler.IoHandler ):
    """
    Contents model for GlueDb records.

    Defines how data is extracted (read) and loaded (written) for a
    GlueDb record. Supports separate configurations for reading and
    writing operations.
    """

    # for extracting (reading) - inherited from IoHandler
    # uri              : str
    # datahandler      : Optional[ str ] = ""
    # kw               : Optional[ dict ] = Field( default_factory=lambda: {} )

    # for loading (writing)
    uriWrite         : Optional[ str ] = ""
    datahandlerWrite : Optional[ str ] = ""
    kwWrite          : Optional[ dict ] = Field( default_factory=lambda: {} )

    @classmethod
    def fromArgs( cls, uri, datahandler="", kw=None, uriWrite="", datahandlerWrite="", kwWrite=None ):
        """ create the model from args """
        return cls( uri=uri, datahandler=datahandler, kw=kw or {}, uriWrite=uriWrite, datahandlerWrite=datahandlerWrite, kwWrite=kwWrite or {} )

    def extract( self ):
        return self._getExtractor().read()

    def load( self, data ):
        """ the L in ETL - loads the contents into a system """
        return self._getLoader().write( data )

    def acquireExtract( self ):
        return self._getExtractor().acquire()

    def acquireLoad( self ):
        return self._getLoader().acquire()

    def _getExtractor(self):
        return IoModel( **self._getExtractKwargs() )

    def _getLoader(self):
        return IoModel( **self._getLoadKwargs() )

    def _getExtractKwargs( self ):
        return {
            'uri'         : self.uri,
            'datahandler' : self.datahandler,
            'kw'          : self.kw,
        }

    def _getLoadKwargs( self ):
        return {
            'uri'         : self.uriWrite or self.uri,
            'datahandler' : self.datahandlerWrite or self.datahandler,
            'kw'          : self.kwWrite,
        }
