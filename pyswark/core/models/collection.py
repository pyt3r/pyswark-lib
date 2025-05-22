from typing import Any, Union
from pydantic import field_validator
from pyswark.lib.pydantic import base
from pyswark.core.models import primitive


class Base( base.BaseModel ):
    data: Any

    def __init__(self, data):
        return super().__init__( data=data )


class List( Base ):
    data: Union[ list, tuple ]

    @field_validator( 'data' )
    def _data( cls, data ) -> list:
        return [ e.data if isinstance( e, primitive.Base ) else primitive.Infer(e).data for e in data ]


class Tuple( List ):

    @field_validator( 'data' )
    def _data( cls, data ) -> tuple:
        alist = super()._data( data )
        return tuple( alist )


class Set( base.BaseModel ):
    inputs: Union[ list, tuple, set ]

    def __init__(self, inputs):
        return super().__init__( inputs=inputs )

    @field_validator( 'inputs' )
    def _inputs( cls, inputs ) -> list:
        return [ e.data if isinstance( e, primitive.Base ) else primitive.Infer(e).data for e in inputs ]

    @property
    def data(self):
        return set( self.inputs )


class Infer:

    TYPE_MAP = {
        list  : List,
        tuple : Tuple,
        set   : Set,
    }

    def __new__( cls, data ):
        klass = cls.TYPE_MAP.get( type(data), None )

        if not klass:
            raise ValueError( f"cannot infer from type={ type(data) }")

        return klass( data )


