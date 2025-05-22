import unittest

from pyswark.lib.pydantic import ser_des
from pyswark.core.models import primitive


class TestCase(unittest.TestCase):

    def test_int(self):
        model = primitive.Int('1.0')
        self.assertEqual(model.data, 1)

    def test_float(self):
        model = primitive.Float('1.1')
        self.assertEqual(model.data, 1.1)

    def test_string(self):
        model = primitive.String('1.1')
        self.assertEqual(model.data, '1.1')

    def test_bool(self):
        model = primitive.Bool(1.0)
        self.assertEqual(model.data, True)

    def test_ser_des(self):
        model = primitive.Infer('1.0')
        ser = ser_des.toJson( model )
        des = ser_des.fromJson( ser )
        self.assertEqual( model, des )
