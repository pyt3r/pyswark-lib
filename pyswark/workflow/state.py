#%%
from typing import Union, Any
from pydantic import BaseModel
from pyswark.lib.pydantic import base

from pyswark.gluedb import api
from pyswark.core.models.infer import Infer


class Interface:

    def __init__( self, mutable=False ):
        self.mutable = mutable or False
        
    def extract(self, name: str ):
        """ extracts the data from the state """

    def post( self, name: str, data: Any ):
        """ posts the data into the state """

    def delete( self, name: str ):
        """ deletes the data from the state """

    def __contains__( self, *a, **kw ):
        """ checks if the state contains the data """
        return super().__contains__( *a, **kw )


class State( Interface, dict ):

    def __init__( self, *a, **kw ):
        Interface.__init__( self, kw.pop( 'mutable', False ))
        dict.__init__( self, *a, **kw )

    def extract( self, name: str ):
        return self[ name ]
    
    def post( self, name: str, data: Any ):
        """
        posts the data into the state.
        If the state is immutable, the data is validated to ensure that it does not contain any keys that are already in the state.
        """
        if not self.mutable:
            if name in self:
                raise ValueError( f"Cannot mutate key: {name}" )

        self[ name ] = data

    def delete( self, name: str ):
        """ deletes the data from the state """
        del self[ name ]


class StateWithGlueDb( Interface ):

    def __init__( self, *args: tuple[dict], **kw ):
        Interface.__init__( self, kw.pop( 'mutable', False ) )
        dicts = args + ( kw, )
        self.db = api.newDb()        
        [ self.post( k, v ) for d in dicts for k, v in d.items() ]
                
    def extract( self, name: str ):
        return self.db.extract( name )
    
    def post( self, name: str, data: Any ):

        if not isinstance( data, BaseModel ):
            data = Infer( data )

        if name in self and self.mutable:
            self.db.put( name, data )
        else:
            self.db.post( name, data )

    def delete( self, name: str ):
        """ deletes the data from the state """
        self.db.delete( name )

    def __contains__( self, name: str ):
        """ checks if the state contains the data """
        return name in self.db