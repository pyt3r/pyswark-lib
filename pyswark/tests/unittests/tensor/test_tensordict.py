import unittest
import numpy as np

from pyswark.tensor.tensordict import TensorDict, VectorDict, MatrixDict
from pyswark.lib.pydantic import ser_des


class TensorDictTestCases( unittest.TestCase ):

    def test_tensor(self):

        model = TensorDict({'a': [
            [[1,2,3], [3,4,5]],
        ]})
        self.assertTupleEqual( model['a'].shape, (1,2,3) )

    def test_ser_des(self):

        model = TensorDict({
            'a': [ [[1,2,3], [3,4,5]], ],
            'b': [ [['A', 'B', 'C'], ['X', 'Y', 'Z']], ]
        })

        ser = ser_des.toJson(model)
        des = ser_des.fromJson(ser)

        np.testing.assert_array_equal( model['b'], des['b'] )


class VectorDictTestCases(unittest.TestCase):

    def test_from_list_1(self):
        model = VectorDict({ 'a': [1, 2, 3] })
        self.assertIsInstance(model['a'], np.ndarray)
        self.assertEqual( model['a'].dtype, np.int64 )

    def test_from_list_2(self):
        with self.assertRaises( ValueError ):
            VectorDict({ 'a': [[1, 2, 3]] })

    def test_from_list_and_dtype(self):
        model = VectorDict({ 'a': { "data": [1, 2, 3], "dtype": float }})
        self.assertIsInstance( model['a'], np.ndarray )
        self.assertEqual( model['a'].dtype, np.float64 )

    def test_from_ndarray(self):
        model = VectorDict({ 'a': np.array([1, 2, 3]) })
        self.assertIsInstance( model['a'], np.ndarray )
        self.assertEqual( model['a'].dtype, np.int64 )

    def test_ser_des(self):
        model = VectorDict({ 'a': np.array([1, 2, 3]) })
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        np.testing.assert_array_equal( model['a'], des['a'] )

    def test_bad_shape(self):
        with self.assertRaises( ValueError ):
            VectorDict({ 'a': [[1,2], [3,4]] })


class MatrixDictTestCases(unittest.TestCase):

    def test_bad_shape(self):
        with self.assertRaises( ValueError ):
            MatrixDict({'a': [1, 2, 3]})

