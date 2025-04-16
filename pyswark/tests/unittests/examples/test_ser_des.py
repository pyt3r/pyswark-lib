import unittest
from pyswark.examples import ser_des


class SmokeTest(unittest.TestCase):

    def test_native(self):
        ser_des.nativePydantic()

    def test_trick_1(self):
        ser_des.pydanticWithATrick1()

    def test_trick_2(self):
        ser_des.pydanticWithATrick2()