import unittest
import tempfile
import pathlib
import shutil
import pandas

from pyswark.lib.pydantic import ser_des

from pyswark.core.models import primitive, collection, infer
from pyswark.core.io import api as io_api

from pyswark.gluedb import api
from pyswark.gluedb import db as db_module
from pyswark.gluedb.models import iomodel
from pyswark.gluedb.db import Db
from pyswark.gluedb.models.iomodel import IoModel


def buildDB_1():
    """Build DB_1 with records 'a' and 'b' containing test dictionaries."""
    db = db_module.Db()
    db.post(collection.Dict({'a': 1}), name='a')
    db.post(collection.Dict({'b': 2, 'c': 3}), name='b')
    return db


def buildDB_2():
    """Build DB_2 with records 'c' and 'd' containing test dictionaries."""
    db = db_module.Db()
    db.post(collection.Dict({'d': 4, 'e': 5, 'f': 6}), name='c')
    db.post(collection.Dict({'g': 7, 'h': 8, 'i': 9}), name='d')
    return db


class TestLocalExample( unittest.TestCase ):

    def setUp(self):
        """Set up test databases in temp files."""
        self.tempdir = tempfile.mkdtemp()
        
        # Create DB_1 and save to file
        db_1 = buildDB_1()
        self.db_1_path = pathlib.Path(self.tempdir) / 'db_1.gluedb'
        io_api.write(db_1, f'file://{self.db_1_path}')
        self.db_1_uri = self.db_1_path.as_uri()
        
        # Create DB_2 and save to file
        db_2 = buildDB_2()
        self.db_2_path = pathlib.Path(self.tempdir) / 'db_2.gluedb'
        io_api.write(db_2, f'file://{self.db_2_path}')
        self.db_2_uri = self.db_2_path.as_uri()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.tempdir)

    def test_acquiring_content_from_a_gluedb(self):
        db = api.connect(f'file://{self.db_2_path}')

        record = db.get( "d" )
        d = record.acquire().extract()
        self.assertDictEqual( d, {'g': 7, 'h': 8, 'i': 9} )

    def test_loading_content_from_a_gluedb(self):
        db = api.connect(f'file://{self.db_2_path}')

        c   = db.extract( "c" )
        d   = db.extract( "d" )

        self.assertDictEqual( c, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( d, {'g': 7, 'h': 8, 'i': 9} )
        
        # Test string reading with datahandler='string'
        # Create a JSON string file
        json_path = pathlib.Path(self.tempdir) / 'test_data.json'
        json_path.write_text('{"x": 1, "y": 2}')
        
        # Post the JSON file path as a string
        db_new = db_module.Db()
        db_new.post(str(json_path), name='json_data')
        
        # Verify it was read and stored correctly
        json_data = db_new.extract('json_data')
        self.assertDictEqual(json_data, {'x': 1, 'y': 2})

    def test_ser_des(self):
        db = api.connect(f'file://{self.db_1_path}')

        ser = db.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual( db.extract('a'), des.extract('a') )

    def test_ser_des_using_a_uri_to_set_the_record(self):
        db = api.connect(f'file://{self.db_1_path}')

        obj = db.get('a').acquire()

        db.delete( 'a' )
        db.post( name='a', obj=obj )

        ser = db.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual( db.extract('a'), des.extract('a') )


class TestCRUD( unittest.TestCase ):

    def setUp(self):
        """Set up test database."""
        self.tempdir = tempfile.mkdtemp()
        db_2 = buildDB_2()
        self.db_2_path = pathlib.Path(self.tempdir) / 'db_2.gluedb'
        io_api.write(db_2, f'file://{self.db_2_path}')

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.tempdir)

    def test_POST_content_in_a_db(self):
        old = api.connect(f'file://{self.db_2_path}')

        db = db_module.Db()
        db.merge( old )

        record = db.get("c")
        db.post(record.acquire(), name='c.copy.1')
        db.post(record.body, name='c.copy.2')

        c_orig  = db.extract('c')
        c_copy1 = db.extract('c.copy.1')
        c_copy2 = db.extract('c.copy.2')

        self.assertListEqual( db.getNames(), ['c', 'd', 'c.copy.1', 'c.copy.2'] )
        self.assertDictEqual( c_orig, c_copy1 )
        self.assertDictEqual( c_copy1, c_copy2 )
        
        # Test merge type checking
        with self.assertRaises(TypeError) as ctx:
            db.merge("not a db")
        self.assertIn("can only merge type Db", str(ctx.exception))

    def test_POST_duplicate_names_in_a_db(self):

        db = db_module.Db()
        db.post( infer.Infer('1'), name='a' )

        with self.assertRaises( Exception ):
            db.post( infer.Infer('2'), name='a' )
        
    def test_PUT_content_in_a_db(self):
        db = api.connect(f'file://{self.db_2_path}')

        old = db.extract( "c" )

        db.put( db.get("d").body, name="c" )
        new = db.extract( "c" )

        self.assertDictEqual( old, {'d': 4, 'e': 5, 'f': 6} )
        self.assertDictEqual( new, {'g': 7, 'h': 8, 'i': 9} )

    @staticmethod
    def makeTestDb():
        db_1 = buildDB_1()
        db_2 = buildDB_2()

        db = db_module.Db()
        db.merge( db_1 )
        db.merge( db_2 )
        return db



class TestPrimitivesAndCollections( unittest.TestCase ):

    def test_adding_primitive_and_collection_models(self):
        db = db_module.Db()
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
        db = db_module.Db()
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
        db = db_module.Db()
        
        contents = IoModel.fromArgs( self.uri, '', {}, '', '', {'overwrite' : True} )
        db.post( name='mydata', obj=contents )

        DF = db.extract('mydata')
        pandas.testing.assert_frame_equal( DF, self.DF )

        DF['x'] = [4,5,6]
        db.load( DF, 'mydata' )   

        DF = db.extract('mydata')
        expected = pandas.DataFrame({'a': [1,2,3], 'x': [4,5,6]})
        pandas.testing.assert_frame_equal( DF, expected )


class TestDbTypeSafe(unittest.TestCase):
    """
    Tests for the Db class - type-safe GlueDb database.
    
    Db extends the base Db class with restrictions on what can be posted.
    This ensures data integrity and enforces the GlueDb data model.
    """

    def setUp(self):
        """Create a temporary directory for test files."""
        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tempdir)

    def test_post_iomodel_and_retrieve(self):
        """
        Post an IoModel and retrieve it by name.
        
        IoModel is the primary way to store references to external data sources.
        This enables the "data as configuration" pattern - store where data lives,
        not the data itself.
        """
        db = Db()
        
        # Create a CSV file
        csv_path = pathlib.Path(self.tempdir) / 'stocks.csv'
        df = pandas.DataFrame({
            'symbol': ['AAPL', 'MSFT'],
            'price': [150.0, 300.0]
        })
        df.to_csv(csv_path, index=True)
        
        # Post an IoModel pointing to the CSV
        model = IoModel.fromArgs(str(csv_path))
        rec = db.post(model, name='stocks')
        
        self.assertIsNotNone(rec)
        self.assertEqual(rec.info.name, 'stocks')
        
        # Retrieve and extract the data
        retrieved = db.getByName('stocks')
        self.assertIsNotNone(retrieved)
        
        # Extract the IoModel and then the data
        iomodel = retrieved.body.extract()
        self.assertIsInstance(iomodel, IoModel)
        
        data = iomodel.extract()
        pandas.testing.assert_frame_equal(data, df)
        
        # Test Path object conversion
        csv_path2 = pathlib.Path(self.tempdir) / 'stocks2.csv'
        df2 = pandas.DataFrame({'symbol': ['GOOGL'], 'price': [2500.0]})
        df2.to_csv(csv_path2, index=True)
        
        # Post using Path object directly (should be converted to string)
        rec2 = db.post(csv_path2, name='stocks2')
        self.assertIsNotNone(rec2)
        data2 = db.extract('stocks2')
        pandas.testing.assert_frame_equal(data2, df2)

    def test_post_primitive_values(self):
        """
        Post primitive values (int, float, str, bool) using primitive.Base.
        
        Primitives are useful for storing simple configuration values,
        metadata, or single values that don't need external storage.
        """
        db = Db()
        
        # Post different primitive types
        db.post(primitive.Int(42), name='answer')
        db.post(primitive.Float(3.14), name='pi')
        db.post(primitive.String('hello'), name='greeting')
        db.post(primitive.Bool(True), name='enabled')
        
        # Retrieve and verify
        answer = db.getByName('answer')
        self.assertEqual(answer.body.extract().extract(), 42)
        
        pi = db.getByName('pi')
        self.assertEqual(pi.body.extract().extract(), 3.14)
        
        greeting = db.getByName('greeting')
        self.assertEqual(greeting.body.extract().extract(), 'hello')
        
        enabled = db.getByName('enabled')
        self.assertEqual(enabled.body.extract().extract(), True)

    def test_post_collection_values(self):
        """
        Post collection values (list, dict) using collection.Base.
        
        Collections enable storing structured data directly in the database
        without requiring external files. Useful for small datasets or
        configuration objects.
        """
        db = Db()
        
        # Post a list
        db.post(collection.List([1, 2, 3]), name='numbers')
        
        # Post a dict
        db.post(collection.Dict({'a': 1, 'b': 2}), name='config')
        
        # Retrieve and verify
        numbers = db.getByName('numbers')
        self.assertEqual(numbers.body.extract().extract(), [1, 2, 3])
        
        config = db.getByName('config')
        self.assertEqual(config.body.extract().extract(), {'a': 1, 'b': 2})

    def test_rejects_disallowed_types(self):
        """
        Db rejects types that are not in AllowedInstances.
        
        This type safety ensures that only approved data models can be stored,
        preventing accidental storage of incompatible types.
        """

        class X:
            pass

        db = Db()
                
        # Try to post a regular BaseModel (not allowed)
        with self.assertRaises(NotImplementedError) as ctx:
            db.post(X(), name='test')
        
        # Should mention it's not an allowed subclass
        self.assertIn('not implemented for type ', str(ctx.exception))

    def test_full_etl_workflow(self):
        """
        Complete ETL workflow: extract, modify, load.
        
        This demonstrates the full power of GlueDb: store a reference to data,
        extract it, modify it, and load it back - all through the database.
        """
        db = Db()
        
        # Create initial CSV
        csv_path = pathlib.Path(self.tempdir) / 'sales.csv'
        initial_df = pandas.DataFrame({
            'product': ['A', 'B'],
            'sales': [100, 200]
        })
        initial_df.to_csv(csv_path, index=True)
        
        # Post IoModel reference
        model = IoModel.fromArgs(str(csv_path), kwWrite={'overwrite': True})
        db.post(model, name='sales')
        
        # Extract, modify, and load
        record = db.getByName('sales')
        iomodel = record.body.extract()
        
        df = iomodel.extract()
        df['sales'] = df['sales'] * 1.1  # 10% increase
        iomodel.load(df)
        
        # Verify changes persisted
        updated_record = db.getByName('sales')
        updated_iomodel = updated_record.body.extract()
        updated_df = updated_iomodel.extract()
        
        expected = pandas.DataFrame({
            'product': ['A', 'B'],
            'sales': [110.0, 220.0]
        })
        pandas.testing.assert_frame_equal(updated_df, expected)
        
        # Test acquireExtract and acquireLoad methods
        df_extracted = db.acquireExtract('sales').read()
        pandas.testing.assert_frame_equal(df_extracted, expected)
        
        # Modify and load using acquireLoad
        df_extracted['sales'] = df_extracted['sales'] * 1.05  # 5% more
        db.acquireLoad('sales').write(df_extracted, overwrite=True)
        
        # Verify changes
        final_df = db.acquireExtract('sales').read()
        expected_final = pandas.DataFrame({
            'product': ['A', 'B'],
            'sales': [115.5, 231.0]
        })
        pandas.testing.assert_frame_equal(final_df, expected_final)

    def test_delete_and_repost(self):
        """
        Delete a record and repost with the same name.
        
        This verifies that deletion works correctly and names can be reused,
        which is important for update workflows.
        """
        db = Db()
        
        # Post a primitive
        db.post(primitive.String('original'), name='value')
        
        # Verify it exists
        self.assertIsNotNone(db.getByName('value'))
        
        # Delete it
        result = db.deleteByName('value')
        self.assertTrue(result)
        self.assertIsNone(db.getByName('value'))
        
        # Repost with same name
        db.post(primitive.String('updated'), name='value')
        
        # Verify new value
        record = db.getByName('value')
        self.assertEqual(record.body.extract().extract(), 'updated')
