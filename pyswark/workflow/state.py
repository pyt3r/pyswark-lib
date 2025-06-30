from typing import Union, Any
from pyswark.lib.pydantic import base


class State( dict ):

    def __init__( self, *a, mutable=False, **kw ):
        super().__init__( *a, **kw )
        self.mutable = mutable

    def extract( self, names: Union[ str, list[ str ]] ):
        """
        Extracts the values from the state for the given names.
        If a single name is provided, the value is returned.
        If a list of names is provided, a list of values is returned.
        """
        isList = isinstance( names, list )
        names = names if isList else [ names ]
        extracted = self._extract( names )
        return extracted if isList else extracted.pop()
    
    def _extract( self, names: list[ str ] ):
        return [ self[name] for name in names ]

    def load( self, data: dict[ str, Any ] ):
        """
        Loads the data into the state.
        If the state is immutable, the data is validated to ensure that it does not contain any keys that are already in the state.
        """
        self._validateDataForLoad( data )
        super().update( **data )

    def _validateDataForLoad( self, data: dict[ str, Any ] ):
        if not self.mutable:
            err = sorted( set( data.keys() ) & set( super().keys() ) )
            if err:
                raise ValueError( f"Cannot mutate keys: {err}" )
