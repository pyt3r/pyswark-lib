from pyswark.lib.pydantic import base
from pyswark.core.io import api as io


class ExtractModel( base.BaseModel ):
    """Reads data from a URI and returns it."""

    uri: str

    def run( self ):
        data = io.read( self.uri )
        print( data[:100] )
        return { 'data': data }
