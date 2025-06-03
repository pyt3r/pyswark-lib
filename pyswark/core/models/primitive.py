from typing import Any, Union
from pyswark.core.models import extractor


class Base( extractor.Extractor ):
    inputs : Any

    def __init__( self, inputs ):
        return super().__init__( inputs=inputs )

    def extract(self):
        return self.inputs


class Int( Base ):
    inputs: int


class Float( Base ):
    inputs: float


class String( Base ):
    inputs: str


class Bool( Base ):
    inputs: bool


class Infer:

    TYPE_MAP = {
        int   : Int,
        float : Float,
        str   : String,
        bool  : Bool,
    }

    @classmethod
    def inScope( cls, inputs ):
        if type( inputs ) in list( cls.TYPE_MAP.keys() ):
            return True

    def __new__( cls, inputs ):
        klass = cls.TYPE_MAP.get( type(inputs), None )

        if not klass:
            raise ValueError( f"cannot infer from type={ type(inputs) }")

        return klass( inputs )

