import unittest
import pydantic
from pyswark.gluedb.recordmodel import Record, Contents, makeRecord
from pyswark.lib.pydantic import ser_des


class CasesWithoutValidation( unittest.TestCase ):

    def test_load_a_record_via_model_without_validation(self):
        body   = ModelXYZ( x=1, y=2, z=3 )
        record = Record( body )
        loaded = record.load()
        self.assertEqual( body.sum(), loaded.sum() )

    def test_load_a_record_via_contents_without_validation(self):
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
        record = RecordABC( body )
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


class CasesWithValidation( unittest.TestCase ):

    def test_load_a_record_via_contents_with_validation(self):
        body   = ContentsABC( a=1, b=2, c=3 )
        record = RecordABC( body )
        loaded = record.load()
        self.assertEqual( -6, loaded )

    def test_ser_des_of_contents(self):
        body   = ContentsABC( a=1, b=2, c=3 )
        record = RecordABC( body )
        ser    = record.toJson()
        des    = ser_des.fromJson( ser )
        loaded = des.load()
        self.assertEqual( body.load(), loaded )

    def test_invalid_contents(self):
        body = Contents()

        with self.assertRaises( ValueError ):
            record = RecordABC( body )


_RecordABC = makeRecord( ContentsABC )


class RecordABC( _RecordABC ):

    @classmethod
    def validate( cls, body ):
        expected = cls.Contents.getUri()
        model    = body['model']
        if model != expected:
            raise ValueError( f"contents has invalid uri: expected model='{expected}', got {model=}" )
