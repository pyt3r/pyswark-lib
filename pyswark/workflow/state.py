from typing import Union, Any
from pydantic import BaseModel, Field
from pyswark.lib.pydantic import base

from pyswark.gluedb import api, db
from pyswark.core.models.infer import Infer


class Interface( base.BaseModel ):
    backend : dict = Field( default_factory=dict )
    mutable : bool = False
    
    def __init__( self, backend=None, **kw ):
        super().__init__( backend=backend or {}, **kw )

    def extract(self, name: str ):
        """ extracts the data from the state """

    def post( self, data: Any, name: str ):
        """ posts the data into the state """

    def delete( self, name: str ):
        """ deletes the data from the state """

    def __contains__( self, *a, **kw ):
        """ checks if the state contains the data """
        return super().__contains__( *a, **kw )


class State( Interface ):

    def extract( self, name: str ):
        return self.backend[ name ]
    
    def post( self, data: Any, name: str ):
        """
        posts the data into the state.
        If the state is immutable, the data is validated to ensure that it does not contain any keys that are already in the state.
        """
        if not self.mutable:
            if name in self.backend:
                raise ValueError( f"Cannot mutate key: {name}" )

        self.backend[ name ] = data

    def delete( self, name: str ):
        """ deletes the data from the state """
        del self.backend[ name ]


class StateWithGlueDb( Interface ):
    backend : db.Db = Field( default_factory=dict )

    def __init__( self, backend=None, **kw ):
        backend = backend or {}
        isDict  = isinstance( backend, dict )
        super().__init__( backend=api.newDb() if isDict else backend, **kw )
        if isDict:
            [ self.post( v, name=k ) for k, v in backend.items() ]

    def extract( self, name: str ):
        return self.backend.extract( name )
    
    def post( self, data: Any, name: str ):

        if not isinstance( data, BaseModel ):
            data = Infer( data )

        if name in self and self.mutable:
            self.backend.put( data, name=name )
        else:
            self.backend.post( data, name=name )

    def delete( self, name: str ):
        """ deletes the data from the state """
        self.backend.delete( name )

    def __contains__( self, name: str ):
        """ checks if the state contains the data """
        return name in self.backend
