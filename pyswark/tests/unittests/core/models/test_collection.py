import unittest

from pyswark.lib.pydantic import ser_des
from pyswark.core.models import collection, primitive


class TestCase(unittest.TestCase):

    def test_tuple(self):
        model = collection.Tuple([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        self.assertTupleEqual( model.load(), (False, 1, True, 1.0, 1.0, '1.0') )

    def test_dict(self):
        model = collection.Dict({ 1:2, '3': ( primitive.Bool(0), )})
        self.assertDictEqual( model.load(), { 1:2, '3': ( False, )})

    def test_ser_des_of_dict(self):
        model = collection.Dict({ 1:2, '3': ( primitive.Bool(0), )})
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertDictEqual( model.load(), des.load() )

    def test_ser_des_of_tuple(self):
        model = collection.Tuple([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertTupleEqual( model.load(), des.load() )

    def test_ser_des_of_set(self):
        model = collection.Set([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertSetEqual( model.load(), des.load() )

    def test_list_of_lists(self):
        model = collection.List([ False, ])
        model = collection.List([[[ model, ], model, ], model, ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertListEqual( model.load(), des.load() )

    def test_tuple_of_tuples(self):
        model = collection.Tuple(( False, ))
        model = collection.Tuple(((( model, ), model, ), model, ))
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertTupleEqual( model.load(), des.load() )





