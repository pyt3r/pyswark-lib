import unittest

from pyswark.lib.pydantic import ser_des

from pyswark.gluedb import api
from pyswark.tests.unittests.data.gluedb.settings import Settings


class TestLocalExample( unittest.TestCase ):

    def test_view_available_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.load(uri)

        self.assertListEqual( db.getNames(), ['c', 'd'] )

        records = db.model_dump()['records']
        bodies  = [ r['body'] for r in records ]

        self.assertListEqual( bodies, [
            { 'model'   : db.Contents.getUri(),
              'contents': { 'uri': f'{ Settings.OBJECTS.uri }.C' }
             },
            { 'model'   : db.Contents.getUri(),
              'contents': { 'uri': f'{ Settings.OBJECTS.uri }.D' }
             },
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

    def test_ser_des_using_a_uri_to_set_the_record(self):
        uri = f'{ Settings.DB.uri }.DB_1'
        db  = api.load(uri)

        uri = db.get('a').body['contents']['uri']

        db.delete( 'a' )
        db.post( 'a', uri )

        ser = db.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual( db.load('a'), des.load('a') )

class TestCRUD( unittest.TestCase ):

    def test_POST_content_in_a_db(self):

        uri = f'{ Settings.DB.uri }.DB_2'
        old = api.load( uri )

        db = api.newDb()
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
        db = api.load(f'{ Settings.DB.uri }.DB_2')

        old = db.load( "c" )

        db.put( "c", db.get("d").body )
        new = db.load( "c" )

        self.assertDictEqual( old, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( new, {'g': 7, 'h': 8, 'i': 9} )

    @staticmethod
    def makeTestDb():
        db_1 = api.load(f'{ Settings.DB.uri }.DB_1')
        db_2 = api.load(f'{ Settings.DB.uri }.DB_2')

        db = api.newDb()
        db.merge( db_1 )
        db.merge( db_2 )
        return db

    def test_exampleDb_creation_without_DELETE(self):
        db = self.makeTestDb()
        self.assertListEqual( db.getNames(), ['a','b','c','d'] )

        infoBody = db.backend.selectInfoAndBody()
        nameIxMap = { info.name : info.index for info, body in infoBody }
        nameIdMap = { info.name : info.id for info, body in infoBody }
        self.assertDictEqual( nameIxMap, { 'a': 0, 'b': 1, 'c': 2, 'd': 3 })
        self.assertDictEqual( nameIdMap, { 'a': 1, 'b': 2, 'c': 3, 'd': 4 })

    def test_DELETE_one_name_from_exampleDb(self):
        db = self.makeTestDb()
        db.delete( 'b' )
        self.assertListEqual( db.getNames(), ['a','c','d'] )

        infoBody  = db.backend.selectInfoAndBody()
        nameIxMap = { info.name : info.index for info, body in infoBody }
        nameIdMap = { info.name : info.id for info, body in infoBody }
        self.assertDictEqual( nameIxMap, {'a': 0, 'c': 1, 'd': 2})
        self.assertDictEqual( nameIdMap, {'a': 1, 'c': 3, 'd': 4})


    def test_DELETE_two_names_from_exampleDb(self):
        db = self.makeTestDb()
        db.delete( 'a' )
        db.delete( 'd' )
        self.assertListEqual( db.getNames(), ['b','c'] )

        infoBody  = db.backend.selectInfoAndBody()
        nameIxMap = { info.name : info.index for info, body in infoBody }
        nameIdMap = { info.name : info.id for info, body in infoBody }
        self.assertDictEqual( nameIxMap, {'b': 0, 'c': 1})
        self.assertDictEqual( nameIdMap, {'b': 2, 'c': 3})