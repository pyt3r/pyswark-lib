import unittest
from pyswark.core.models import contentsmodel


class TestCase( unittest.TestCase ):

    def test_load_contents_of_a_record(self):
        record   = Record( name='abc', contents={'a': 1, 'b': 2, 'c': 3.1})
        contents = record.load()
        self.assertEqual( contents.sum(), 6.1 )


class Contents(contentsmodel.Contents):
    a: int
    b: int
    c: float

    def sum( self ):
        return self.a + self.b + self.c

Record = contentsmodel.makeRecord(Contents)
