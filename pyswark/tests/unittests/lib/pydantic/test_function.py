import unittest
from pydantic import Field, field_validator

from pyswark.lib.pydantic.function import FunctionModel
from pyswark.lib.pydantic import base
from pyswark.lib.pydantic import ser_des


class TestCase(unittest.TestCase):

    def test_function_model_that_multplies_by_10(self):
        model = MultiplyBy10(inputs=Inputs(5))
        self.assertEqual(model.outputs.data, 50)

    def test_ser_des(self):
        model = MultiplyBy10(inputs=5)
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        self.assertEqual( model, des )


class Inputs( base.BaseInputs ):
    data: int

    @field_validator( 'data', mode='before' )
    def _data(cls, data):
        assert float( data ) > 0
        return data

class Outputs( base.BaseOutputs ):
    data: float

class MultiplyBy10( FunctionModel ):
    inputs  : Inputs
    outputs : Outputs = Field(default=None, description="")

    @staticmethod
    def function( inputs: Inputs ):
        return inputs.data * 10
