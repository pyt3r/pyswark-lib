import unittest
import pydantic

from pyswark.lib.pydantic import base
from pyswark.lib.pydantic.ser_des import toJson, fromJson
from typing import ClassVar


class SerializationTestCases( unittest.TestCase ):

    def test_de_serialization_of_a_basemodel(self):
        data = {
            'b': {'bdata': 1},
            'c': {'cdata': '2'},
        }

        obj = A( **data )
        serialized_1 = toJson( obj )
        serialized_2 = obj.toJson()

        deserialized_1 = fromJson( serialized_1 )
        deserialized_2 = fromJson( serialized_2 )

        self.assertEqual( obj, deserialized_1 )
        self.assertEqual( obj, deserialized_2 )


    def test_de_serialization_of_a_rootmodel(self):
        data = {
            'b': {'bdata': 1},
            'c': {'cdata': '2'},
        }

        obj = RootModel( **data )
        serialized = toJson( obj )
        deserialized = fromJson( serialized )

        self.assertEqual( obj, deserialized )


class B( base.BaseModel ):
    bdata: int


class C( base.BaseModel ):
    cdata: float


class A( base.BaseModel ):
    b: B
    c: C

    x: ClassVar = 1

    def y( self ):
        pass


class RootModel( pydantic.RootModel ):
    root: A
