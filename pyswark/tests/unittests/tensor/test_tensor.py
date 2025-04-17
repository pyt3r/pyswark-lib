import unittest
import numpy as np

from pyswark.tensor.tensor import Tensor, Vector, Matrix
from pyswark.lib.pydantic import ser_des


class TensorTestCases( unittest.TestCase ):

    def test_tensor(self):
        model = Tensor([
            [[1,2,3], [3,4,5]],
        ])
        self.assertTupleEqual( model.shape, (1,2,3) )

class VectorTestCases(unittest.TestCase):

    def test_from_list_1(self):
        model = Vector([1, 2, 3])
        self.assertIsInstance(model.vector, np.ndarray)

    def test_from_list_2(self):
        with self.assertRaises( ValueError ):
            Vector([[ 1, 2, 3 ]])

    def test_from_list_and_dtype(self):
        model = Vector({"data": [1, 2, 3], "dtype": float})
        self.assertIsInstance(model.vector, np.ndarray)

    def test__from_ndarray(self):
        model = Vector(np.array([1, 2, 3]))
        self.assertIsInstance(model.vector, np.ndarray)

    def test_ser_des(self):
        model = Vector( np.array([1, 2, 3]) )
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        np.testing.assert_array_equal(model.vector, des.vector)

    def test_ser_des_string(self):
        model = Vector( ['a', 'b', 'c'] )
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        np.testing.assert_array_equal(model.vector, des.vector)

    def test_bad_shape(self):
        with self.assertRaises( ValueError ):
            Vector([[1,2], [3,4]])


class MatrixTestCases(unittest.TestCase):

    def test_bad_shape(self):
        with self.assertRaises( ValueError ):
            Matrix([1, 2, 3])

