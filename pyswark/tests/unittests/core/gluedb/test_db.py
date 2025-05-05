import unittest

from pyswark.lib.pydantic import ser_des

from pyswark.core.gluedb import api
from pyswark.examples.gluedb.settings import Settings


class TestLocalExample( unittest.TestCase ):

    def test_view_available_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.load(uri)

        self.assertListEqual( db.getNames(), ['c', 'd'] )

        self.assertListEqual( db.model_dump()['records'], [
            {'info' : {'name': 'c'},
             'body' : {
                'model'   : db.Contents.getUri(),
                'contents': { 'uri': f'{ Settings.OBJECTS.uri }.C' }
             }},
            {'info' : {'name': 'd'},
             'body' : {
                 'model'   : db.Contents.getUri(),
                 'contents': { 'uri': f'{ Settings.OBJECTS.uri }.D' }
             }},
        ])

    def test_acquiring_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.load(uri)

        record = db.get( "d" )

        contents = record.get()
        self.assertDictEqual( contents.model_dump(),
            {'uri': f'{ Settings.OBJECTS.uri }.D', 'datahandler': '', 'kw': {}}
        )

        d = record.load()
        self.assertDictEqual( d, {'g': 7, 'h': 8, 'i': 9} )

    def test_loading_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.load(uri)

        c   = db.load( "c" )
        d   = db.load( "d" )

        self.assertDictEqual( c, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( d, {'g': 7, 'h': 8, 'i': 9} )

    def test_ser_des(self):
        uri = f'{ Settings.DB.uri }.DB_1'
        db  = api.load(uri)

        ser = db.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual( db.load('a'), des.load('a') )


class TestCRUD( unittest.TestCase ):

    def test_POST_content_in_a_db(self):

        old = api.load(f'{ Settings.DB.uri }.DB_2')

        db = api.new()
        db.merge( old )

        record = db.get("c")
        db.post('c.copy.1', record.model_dump()['body'])
        db.post('c.copy.2', record.body)

        c_orig  = db.load('c')
        c_copy1 = db.load('c.copy.1')
        c_copy2 = db.load('c.copy.2')

        self.assertListEqual( db.getNames(), ['c', 'd', 'c.copy.1', 'c.copy.2'] )
        self.assertDictEqual( c_orig, c_copy1 )
        self.assertDictEqual( c_copy1, c_copy2 )

    def test_PUT_content_in_a_db(self):
        pass

    def test_DELETE_content_in_a_db(self):
        pass

