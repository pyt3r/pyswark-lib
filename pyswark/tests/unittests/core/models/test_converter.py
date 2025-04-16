import unittest
import numpy as np
from typing import List

from pyswark.lib.pydantic import ser_des

from pyswark.core.models import xputs
from pyswark.core.models import converter


class TestCase(unittest.TestCase):

    def test_toarray_model(self):
        model = ToArray([1,2,3])
        self.assertIsInstance( model.outputs, np.ndarray )

    def test_ser_des(self):
        model = ToArray([1,2,3])
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        np.testing.assert_array_equal( model.outputs, des.outputs )


class Inputs( xputs.BaseInputs ):
    data: List


class ToArray(converter.ConverterModel):
    inputs: Inputs

    @staticmethod
    def convert( inputs: Inputs ):
        return np.array( inputs.data )
