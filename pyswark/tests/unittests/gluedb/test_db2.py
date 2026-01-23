"""
Tests for pyswark.gluedb.db
=============================

Db provides a type-safe database for GlueDb records with restricted allowed types.
Only IoModel, primitive.Base, and collection.Base instances can be posted.

Key Features
------------
- Type safety: Only approved types can be stored
- IoModel support: Store references to external data sources
- Primitive support: Store simple values (int, float, str, bool)
- Collection support: Store lists, dicts, and other collections

Example Usage
-------------
>>> from pyswark.gluedb.db import Db
>>> from pyswark.gluedb.models.iomodel import IoModel
>>> from pyswark.core.models import primitive
>>>
>>> db = Db()
>>> 
>>> # Post an IoModel (reference to external data)
>>> model = IoModel.fromArgs('file:./data.csv')
>>> db.post(model, name='mydata')
>>>
>>> # Post a primitive value
>>> db.post(primitive.Int(42), name='answer')
>>>
>>> # Retrieve records
>>> record = db.getByName('mydata')
"""

import unittest
import tempfile
import pathlib
import shutil

import pandas

from pyswark.gluedb.db import Db
from pyswark.gluedb.models.iomodel import IoModel
from pyswark.core.models import primitive, collection
from pyswark.lib.pydantic import base


class TestDb(unittest.TestCase):
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



if __name__ == '__main__':
    unittest.main()
