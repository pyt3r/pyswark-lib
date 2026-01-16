import unittest
import tempfile
import pathlib
import shutil
import pandas

from pyswark.lib.pydantic import ser_des

from pyswark.core.models import primitive, collection, infer

from pyswark.gluedb import api
from pyswark.gluedb.models import IoModel

from pyswark.tests.unittests.data.gluedb.settings import Settings


class TestLocalExample( unittest.TestCase ):


    def test_acquiring_content_from_a_gluedb(self):
        uri = f'{ Settings.DB.uri }.DB_2'
        db  = api.connect(uri)

        record = db.get( "d" )
        d = record.acquire().extract()
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

        uri = db.get('a').acquire().uri

        db.delete( 'a' )
        db.post( name='a', obj=uri )

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
        db.post(record.body.contents, name='c.copy.1')
        db.post(record.body, name='c.copy.2')

        c_orig  = db.extract('c')
        c_copy1 = db.extract('c.copy.1')
        c_copy2 = db.extract('c.copy.2')

        self.assertListEqual( db.getNames(), ['c', 'd', 'c.copy.1', 'c.copy.2'] )
        self.assertDictEqual( c_orig, c_copy1 )
        self.assertDictEqual( c_copy1, c_copy2 )

    def test_POST_duplicate_names_in_a_db(self):

        db = api.newDb()
        db.post( infer.Infer('1'), name='a' )

        with self.assertRaises( Exception ):
            db.post( infer.Infer('2'), name='a' )
        
    def test_PUT_content_in_a_db(self):
        db = api.connect(f'{ Settings.DB.uri }.DB_2')

        old = db.extract( "c" )

        db.put( db.get("d").body, name="c" )
        new = db.extract( "c" )

        self.assertDictEqual( old, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( new, {'g': 7, 'h': 8, 'i': 9} )

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
        db.post( name='integer', obj=primitive.Int('1.0'))
        db.post( name='float', obj=primitive.Float('1.0'))
        db.post( name='string', obj=primitive.String('1.0'))
        db.post( name='list', obj=collection.List([1, '1', 1.]))
        db.post( name='dict', obj=collection.Dict([
            ( '1.0', 1.0 ), 
            ( primitive.String('2.0'), primitive.Float('2.0') ),
        ]))
        db.post( name='a string with spaces!', obj=primitive.String('my string'))

        self.assertEqual( db.extract( 'integer' ), 1.0 )
        self.assertEqual( db.extract( 'float' ), 1.0 )
        self.assertEqual( db.extract( 'string' ), '1.0' )
        self.assertEqual( db.extract( 'list' ), [1, '1', 1.] )
        self.assertEqual( db.extract( 'dict' ), { '1.0': 1.0, '2.0': 2.0 } ) 

        self.assertEqual( db.extract( 'a string with spaces!' ), 'my string' ) 
        self.assertEqual( db.extract( db.enum.a_string_with_spaces_.value ), 'my string' ) 

    def test_invalid_and_valid_models(self):
        db = api.newDb()
        db.post( name='valid', obj=infer.Infer('1') )
        
        self.assertEqual( db.extract('valid'), '1' )
        
        with self.assertRaises( NotImplementedError ) as ctx:
            db.post( name='invalid', obj=1 )
        
        self.assertIn( 'post() not implemented for type', str(ctx.exception) )
        

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
        
        contents = IoModel.fromArgs( self.uri, '', {}, '', '', {'overwrite' : True} )
        db.post( name='mydata', obj=contents )

        DF = db.extract('mydata')
        pandas.testing.assert_frame_equal( DF, self.DF )

        DF['x'] = [4,5,6]
        db.load( DF, 'mydata' )   

        DF = db.extract('mydata')
        expected = pandas.DataFrame({'a': [1,2,3], 'x': [4,5,6]})
        pandas.testing.assert_frame_equal( DF, expected )
