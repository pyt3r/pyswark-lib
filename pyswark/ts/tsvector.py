
from pydantic import model_validator, field_validator
from pyswark.lib.pydantic import base

from pyswark.tensor import tensor
from pyswark.ts.datetime import DatetimeList


class TsVector( base.BaseModel ):
    index  : DatetimeList
    values : tensor.Vector

    @property
    def dt(self):
        return self.index.dt

    @field_validator( "index", mode='before' )
    def _index(cls, index ):
        return index if isinstance( index, DatetimeList ) else DatetimeList( index )

    @field_validator( "values", mode='before' )
    def _values(cls, values ):
        return values if isinstance( values, tensor.Vector ) else tensor.Vector( values )

    @model_validator( mode='after' )
    def _after(self):
        if len( self.dt ) != len( self.values ):
            raise ValueError( f"lengths must match: { len( self.dt )= }, { len( self.values )= }" )
        return self
