import unittest

from pyswark.lib.pydantic import ser_des
from pyswark.core.models import collection, primitive


class TestCase(unittest.TestCase):

    def test_tuple(self):
        model = collection.Tuple([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        self.assertTupleEqual(model.data, (False, 1, True, 1.0, 1.0, '1.0'))

    def test_ser_des_of_tuple(self):
        model = collection.Tuple([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        self.assertEqual( model, des )

    def test_ser_des_of_set(self):
        model = collection.Set([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        self.assertEqual( model, des )
