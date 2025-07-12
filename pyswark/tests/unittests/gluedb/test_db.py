import unittest
import tempfile
import pathlib
import shutil
import pandas

from pyswark.lib.pydantic import ser_des

from pyswark.core.models import primitive, collection, infer

from pyswark.gluedb import api
from pyswark.tests.unittests.data.gluedb.settings import Settings


class TestLocalExample( unittest.TestCase ):

    def test_view_available_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.connect(uri)

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
        db  = api.connect(uri)

        record = db.get( "d" )

        contents = record.acquire()
        self.assertDictEqual( contents.model_dump(),
            {'uri': f'{ Settings.OBJECTS.uri }.D', 'datahandler': '', 'kw': {}, 'datahandlerWrite': '', 'kwWrite': {}}
        )

        d = record.extract()
        self.assertDictEqual( d, {'g': 7, 'h': 8, 'i': 9} )

    def test_loading_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.connect(uri)

        c   = db.extract( "c" )
        d   = db.extract( "d" )

        self.assertDictEqual( c, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( d, {'g': 7, 'h': 8, 'i': 9} )

    def test_ser_des(self):
        uri = f'{ Settings.DB.uri }.DB_1'
        db  = api.connect(uri)

        ser = db.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual( db.extract('a'), des.extract('a') )

    def test_ser_des_using_a_uri_to_set_the_record(self):
        uri = f'{ Settings.DB.uri }.DB_1'
        db  = api.connect(uri)

        uri = db.get('a').body['contents']['uri']

        db.delete( 'a' )
        db.post( 'a', uri )

        ser = db.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual( db.extract('a'), des.extract('a') )


class TestCRUD( unittest.TestCase ):

    def test_POST_content_in_a_db(self):

        uri = f'{ Settings.DB.uri }.DB_2'
        old = api.connect( uri )

        db = api.newDb()
        db.merge( old )

        record = db.get("c")
        db.post('c.copy.1', record.model_dump()['body'])
        db.post('c.copy.2', record.body)

        c_orig  = db.extract('c')
        c_copy1 = db.extract('c.copy.1')
        c_copy2 = db.extract('c.copy.2')

        self.assertListEqual( db.getNames(), ['c', 'd', 'c.copy.1', 'c.copy.2'] )
        self.assertDictEqual( c_orig, c_copy1 )
        self.assertDictEqual( c_copy1, c_copy2 )

    def test_POST_duplicate_names_in_a_db(self):

        db = api.newDb()
        db.post( 'a', infer.Infer('1') )

        with self.assertRaises( Exception ):
            db.post( 'a', infer.Infer('2') )
        
    def test_PUT_content_in_a_db(self):
        db = api.connect(f'{ Settings.DB.uri }.DB_2')

        old = db.extract( "c" )

        db.put( "c", db.get("d").body )
        new = db.extract( "c" )

        self.assertDictEqual( old, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( new, {'g': 7, 'h': 8, 'i': 9} )

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

    @staticmethod
    def makeTestDb():
        db_1 = api.connect(f'{ Settings.DB.uri }.DB_1')
        db_2 = api.connect(f'{ Settings.DB.uri }.DB_2')

        db = api.newDb()
        db.merge( db_1 )
        db.merge( db_2 )
        return db



class TestPrimitivesAndCollections( unittest.TestCase ):

    def test_adding_primitive_and_collection_models(self):
        db = api.newDb()
        db.post( 'integer', primitive.Int('1.0'))
        db.post( 'float', primitive.Float('1.0'))
        db.post( 'string', primitive.String('1.0'))
        db.post( 'list', collection.List([1, '1', 1.]))
        db.post( 'dict', collection.Dict([
            ( '1.0', 1.0 ), 
            ( primitive.String('2.0'), primitive.Float('2.0') ),
        ]))
        db.post( 'a string with spaces!', primitive.String('my string'))

        self.assertEqual( db.extract( 'integer' ), 1.0 )
        self.assertEqual( db.extract( 'float' ), 1.0 )
        self.assertEqual( db.extract( 'string' ), '1.0' )
        self.assertEqual( db.extract( 'list' ), [1, '1', 1.] )
        self.assertEqual( db.extract( 'dict' ), { '1.0': 1.0, '2.0': 2.0 } ) 

        self.assertEqual( db.extract( 'a string with spaces!' ), 'my string' ) 
        self.assertEqual( db.extract( db.enum.a_string_with_spaces_.value ), 'my string' ) 

    def test_invalid_and_valid_models(self):
        db = api.newDb()
        db.post( 'valid', infer.Infer('1') )
        db.post( 'invalid', '1' )

        self.assertEqual( db.extract('valid'), '1' )
        
        with self.assertRaisesRegex( ValueError, "Handler not found for uri='1'" ):
            db.extract('invalid')

    def test_pop(self):
        db = api.newDb()
        db.post( 'string', primitive.String('1.0'))

        self.assertTrue( 'string' in db )
        self.assertEqual( db.extract( 'string' ), '1.0' )

        popped = db.pop( 'string' )
        self.assertFalse( 'string' in db )
        self.assertEqual( popped.extract(), '1.0' )

        db = api.newDb()
        db.post( 'popped', popped )
        self.assertEqual( db.extract( 'popped' ), '1.0' )
        

class TestLoad( unittest.TestCase ):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.uri = str( pathlib.Path( self.tempdir ) / 'mydata.csv' )
        
        self.DF = pandas.DataFrame({'a': [1,2,3]})
        self.DF.to_csv( self.uri )

    def tearDown(self):
        shutil.rmtree( self.tempdir )

    def test_load(self):
        db = api.newDb()
        
        contents = db.Contents.fromArgs( self.uri, '', {}, '', {'overwrite' : True} )
        db.post( 'mydata', contents )

        DF = db.extract('mydata')
        pandas.testing.assert_frame_equal( DF, self.DF )

        DF['x'] = [4,5,6]
        db.load( DF, 'mydata' )   

        DF = db.extract('mydata')
        expected = pandas.DataFrame({'a': [1,2,3], 'x': [4,5,6]})
        pandas.testing.assert_frame_equal( DF, expected )
