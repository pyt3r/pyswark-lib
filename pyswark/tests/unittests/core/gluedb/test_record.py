import unittest
import pydantic
from pyswark.core.gluedb.recordmodel import Record, Contents
from pyswark.lib.pydantic import ser_des


class TestCase( unittest.TestCase ):

    def test_load_a_record_via_model(self):
        body   = ModelXYZ( x=1, y=2, z=3 )
        record = Record( body )
        loaded = record.load()
        self.assertEqual( body.sum(), loaded.sum() )

    def test_load_a_record_via_contents(self):
        body   = ContentsABC( a=1, b=2, c=3 )
        record = Record( body )
        loaded = record.load()
        self.assertEqual( -6, loaded )

    def test_ser_des_of_model(self):
        body   = ModelXYZ( x=1, y=2, z=3 )
        record = Record( body )
        ser    = record.toJson()
        des    = ser_des.fromJson( ser )
        loaded = des.load()
        self.assertEqual( body.sum(), loaded.sum() )

    def test_ser_des_of_contents(self):
        body   = ContentsABC( a=1, b=2, c=3 )
        record = Record( body )
        ser    = record.toJson()
        des    = ser_des.fromJson( ser )
        loaded = des.load()
        self.assertEqual( body.load(), loaded )


class ModelXYZ( pydantic.BaseModel ):
    x: int
    y: int
    z: int

    def sum( self ):
        return self.x + self.y + self.z


class ContentsABC( Contents ):
    a: int
    b: int
    c: int

    def load( self ):
        return - ( self.a + self.b + self.c )

    

