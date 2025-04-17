import unittest
import numpy as np

from pyswark.tensor.tensorframe import TensorFrame, VectorFrame
from pyswark.lib.pydantic import ser_des


class TensorFrameTestCases( unittest.TestCase ):

    def test_frame_with_dict_as_input(self):

        frame = TensorFrame({
            'a': [ 1, 2, 3 ],
            'b': [
                [ 'a', 'A' ],
                [ 'b', 'B' ],
                [ 'c', 'C' ],
            ],
        })
        self.assertEqual( len(frame), 3 )
        np.testing.assert_array_equal( frame['a'], np.array([1,2,3]) )
        np.testing.assert_array_equal( frame['b'][0], np.array(['a', 'A']) )

        record = frame.getRecord(0)
        self.assertEqual( record['a'], 1 )
        np.testing.assert_array_equal( record['b'], np.array(['a', 'A']) )

    def test_mismatching_lengths(self):

        with self.assertRaises( ValueError ):
            TensorFrame({
                'a': [ 1, 2, 3 ],
                'b': ['a', 'b'],
            })

    def test_merge(self):

        frame = TensorFrame({
            'a': [ 1, 2, 3 ],
            'b': [
                [ 'a', 'A' ],
                [ 'b', 'B' ],
                [ 'c', 'C' ],
            ],
        })

        other = TensorFrame({
            'c': [ 4, 5, 6 ],
            'd': 'x y z'.split(),
        })

        new = frame.merge( other )

        self.assertListEqual( list(new.keys()), 'a b c d'.split() )

    def test_ser_des(self):

        frame = TensorFrame({
            'a': [ 1, 2, 3 ],
            'b': [
                [ 'a', 'A' ],
                [ 'b', 'B' ],
                [ 'c', 'C' ],
            ],
        })

        ser = ser_des.toJson(frame)
        des = ser_des.fromJson(ser)

        np.testing.assert_array_equal( frame['a'], des['a'] )


class VectorFrameTestCase( unittest.TestCase ):

    def test_ser_des(self):
        frame = VectorFrame({
            'a': [ 1, 2, 3 ],
            'b': [ 'X', 'Y', 'Z'],
        })

        ser = ser_des.toJson(frame)
        des = ser_des.fromJson(ser)

        np.testing.assert_array_equal( frame['a'], des['a'] )

    def test_invalid_shape(self):
        with self.assertRaises( ValueError ):
            VectorFrame({
                'a': [ 1, 2, 3 ],
                'b': [
                    [ 'a', 'A' ],
                    [ 'b', 'B' ],
                    [ 'c', 'C' ],
                ],
            })

    def test_invalid_length(self):
        with self.assertRaises( ValueError ):
            VectorFrame({
                'a': [ 1, 2, 3 ],
                'b': [ 1, 2, ],
            })
