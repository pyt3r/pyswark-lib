from typing import Any, Union
from pyswark.lib.pydantic import base


class Base( base.BaseModel ):
    data: Any

    def __init__( self, data ):
        return super().__init__( data=data )


class Int( Base ):
    data: int


class Float( Base ):
    data: float


class String( Base ):
    data: str


class Bool( Base ):
    data: bool


class Infer:

    TYPE_MAP = {
        int   : Int,
        float : Float,
        str   : String,
        bool  : Bool,
    }

    def __new__( cls, data ):
        klass = cls.TYPE_MAP.get( type(data), None )

        if not klass:
            raise ValueError( f"cannot infer from type={ type(data) }")

        return klass( data )

