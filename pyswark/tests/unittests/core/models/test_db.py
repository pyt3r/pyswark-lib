"""
Tests for pyswark.core.models.db
================================

Db and DbSQLModel provide database persistence for Records.

DbSQLModel wraps SQLModel/SQLAlchemy for storing and retrieving
Records with their nested Info and Body data.

Example Usage
-------------
>>> from pyswark.core.models.db import DbSQLModel
>>> from pyswark.lib.pydantic import base
>>>
>>> class Ticker(base.BaseModel):
...     symbol: str
...     longName: str
...     exchange: str
>>>
>>> db = DbSQLModel()  # in-memory SQLite
>>> aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
>>> db.post(aapl, name='AAPL')
>>> record = db.getByName('AAPL')
"""

import unittest
from pyswark.lib.pydantic import base
from pyswark.core.models.db import Db, DbSQLModel
from pyswark.core.models import record, body


class Ticker(base.BaseModel):
    """
    Sample model representing a stock ticker.
    
    A simple but realistic example of data you'd want to persist.
    """
    symbol   : str
    longName : str
    exchange : str


class TestDb(unittest.TestCase):
    """
    Tests for the Db class (in-memory record collection).
    
    Db uses SQLModel internally via asSQLModel() for persistence operations.
    """

    def test_post_get_and_delete(self):
        """
        Complete workflow: post, retrieve, and delete records.
        
        Covers the full lifecycle: post a model, get it back by name,
        delete it, verify it's gone, and can repost with the same name.
        """
        db = Db()
        
        # Post a ticker
        msft = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
        rec = db.post(msft, name='MSFT')
        
        self.assertIsInstance(rec, record.Record)
        self.assertEqual(rec.info.name, 'MSFT')
        
        # Verify data integrity
        extracted = rec.body.extract()
        self.assertIsInstance(extracted, Ticker)
        self.assertEqual(extracted.symbol, 'MSFT')
        self.assertEqual(extracted.longName, 'Microsoft Corporation')
        
        # Retrieve by name (uses SQLModel internally)
        retrieved = db.getByName('MSFT')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.info.name, 'MSFT')
        
        # Verify retrieved data matches
        retrieved_ticker = retrieved.body.extract()
        self.assertEqual(retrieved_ticker.symbol, 'MSFT')
        self.assertEqual(retrieved_ticker.longName, 'Microsoft Corporation')
        
        # Delete by name
        result = db.deleteByName('MSFT')
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(db.getByName('MSFT'))
        
        # Can repost with same name
        updated = Ticker(symbol='MSFT', longName='Microsoft Corp.', exchange='NASDAQ')
        new_rec = db.post(updated, name='MSFT')
        self.assertIsNotNone(new_rec)
        self.assertIsNotNone(db.getByName('MSFT'))
        
    def test_posting_with_infoKw(self):
        db = Db()

        from pyswark.core.models.info import Info
        from pyswark.core.models.body import Body
        
        ticker = Ticker(symbol='TSLA', longName='Tesla Inc.', exchange='NASDAQ')
        rec = record.Record(
            info=Info(name='TSLA'),
            body=Body(model=ticker, contents='{}')
        )
        
        # Post Record with additional infoKw that should be set on rec.info
        posted_rec = db.post(rec, name='TSLA_CUSTOM', custom_attr='test_value')
        self.assertEqual(posted_rec.info.name, 'TSLA_CUSTOM')
        # Note: custom_attr won't be on Info model, but the code path is tested

    def test_getByName_retrieves_existing_record(self):
        """
        getByName() retrieves a record by name.
        
        This tests the getByName() method which uses SQLModel internally
        via asSQLModel() to query and retrieve records.
        """
        db = Db()
        
        # Post a record
        aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
        db.post(aapl, name='AAPL')
        
        # Retrieve by name
        retrieved = db.getByName('AAPL')
        
        self.assertIsNotNone(retrieved)
        self.assertIsInstance(retrieved, record.Record)
        self.assertEqual(retrieved.info.name, 'AAPL')
        
        # Verify data integrity
        ticker = retrieved.body.extract()
        self.assertIsInstance(ticker, Ticker)
        self.assertEqual(ticker.symbol, 'AAPL')

    def test_getByName_returns_none_for_nonexistent(self):
        """
        getByName() returns None when record doesn't exist.
        
        This ensures safe behavior - no exceptions raised for missing records.
        """
        db = Db()
        
        # Try to get a non-existent record
        result = db.getByName('DOESNOTEXIST')
        
        self.assertIsNone(result)

    def test_deleteByName_removes_record_and_updates_records(self):
        """
        deleteByName() removes a record and updates self.records.
        
        This tests that deleteByName() not only deletes from SQLModel
        but also updates the in-memory records list.
        """
        db = Db()
        
        # Post multiple records
        tickers = [
            Ticker(symbol='JPM', longName='JPMorgan Chase', exchange='NYSE'),
            Ticker(symbol='BAC', longName='Bank of America', exchange='NYSE'),
        ]
        
        for t in tickers:
            db.post(t, name=t.symbol)
        
        # Verify both exist
        self.assertEqual(len(db.records), 2)
        self.assertIsNotNone(db.getByName('JPM'))
        self.assertIsNotNone(db.getByName('BAC'))
        
        # Delete one
        result = db.deleteByName('JPM')
        
        # Verify deletion succeeded
        self.assertTrue(result)
        
        # Verify records list was updated
        self.assertEqual(len(db.records), 1)
        
        # Verify it's gone from database
        self.assertIsNone(db.getByName('JPM'))
        
        # Verify other record still exists
        self.assertIsNotNone(db.getByName('BAC'))

    def test_deleteByName_returns_false_for_nonexistent(self):
        """
        deleteByName() returns False when record doesn't exist.
        
        This ensures safe behavior - no exceptions raised for missing records.
        """
        db = Db()
        
        # Try to delete a non-existent record
        result = db.deleteByName('DOESNOTEXIST')
        
        self.assertFalse(result)
        
        # Verify records list unchanged
        self.assertEqual(len(db.records), 0)

    def test_post_body_requires_name(self):
        """
        Posting a Body directly requires a name parameter.
        
        This covers the validation in _post_body() that ensures
        name is provided when posting a Body instance.
        """
        db = Db()
        
        # Create a Body
        ticker = Ticker(symbol='TEST', longName='Test Corp', exchange='NYSE')
        bod = body.Body(model=ticker)
        
        # Posting without name should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            db.post(bod, name=None)
        
        self.assertIn('name is required', str(ctx.exception))
        self.assertIn('Body', str(ctx.exception))

    def test_post_basemodel_requires_name(self):
        """
        Posting a BaseModel requires a name parameter.
        
        This covers the validation in _post_model() that ensures
        name is provided when posting a BaseModel instance.
        """
        db = Db()
        
        # Create a BaseModel
        ticker = Ticker(symbol='TEST', longName='Test Corp', exchange='NYSE')
        
        # Posting without name should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            db.post(ticker, name=None)
        
        self.assertIn('name is required', str(ctx.exception))
        self.assertIn('Ticker', str(ctx.exception))
        
        # Also test with name not provided at all (defaults to None)
        with self.assertRaises(ValueError) as ctx2:
            db.post(ticker)  # name parameter omitted
        
        self.assertIn('name is required', str(ctx2.exception))
        
    def test_post_fallback_raises(self):
        db = Db()

        class UnsupportedType:
            pass
        
        with self.assertRaises(NotImplementedError) as ctx3:
            db.post(UnsupportedType(), name='unsupported')
        
        self.assertIn('post() not implemented for type', str(ctx3.exception))
        self.assertIn('UnsupportedType', str(ctx3.exception))

    def test_put_creates_new_record(self):
        """
        PUT creates a new record when one doesn't exist.
        
        PUT is idempotent - it works whether the record exists or not.
        When the record doesn't exist, PUT behaves like POST.
        """
        db = Db()
        
        # PUT a new ticker
        aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
        rec = db.put(aapl, name='AAPL')
        
        self.assertIsNotNone(rec)
        self.assertEqual(rec.info.name, 'AAPL')
        
        # Verify it was created
        retrieved = db.getByName('AAPL')
        self.assertIsNotNone(retrieved)
        ticker = retrieved.body.extract()
        self.assertEqual(ticker.symbol, 'AAPL')
        self.assertEqual(ticker.longName, 'Apple Inc.')

    def test_put_updates_existing_record(self):
        """
        PUT updates an existing record by replacing it.
        
        This is the key difference from POST - PUT replaces existing
        records rather than creating duplicates or raising errors.
        """
        db = Db()
        
        # Create initial record
        original = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
        db.post(original, name='MSFT')
        
        # Verify original exists
        retrieved = db.getByName('MSFT')
        self.assertEqual(retrieved.body.extract().longName, 'Microsoft Corporation')
        
        # PUT an updated version
        updated = Ticker(symbol='MSFT', longName='Microsoft Corp.', exchange='NASDAQ')
        db.put(updated, name='MSFT')
        
        # Verify it was updated
        retrieved = db.getByName('MSFT')
        self.assertIsNotNone(retrieved)
        ticker = retrieved.body.extract()
        self.assertEqual(ticker.longName, 'Microsoft Corp.')  # Updated value
        self.assertEqual(ticker.symbol, 'MSFT')  # Same symbol

    def test_put_is_idempotent(self):
        """
        PUT is idempotent - multiple calls with same data produce same result.
        
        This is a key property of PUT operations - calling it multiple
        times should result in the same state as calling it once.
        """
        db = Db()
        
        ticker = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
        
        # PUT multiple times
        db.put(ticker, name='GOOGL')
        db.put(ticker, name='GOOGL')
        db.put(ticker, name='GOOGL')
        
        # Should still have exactly one record
        retrieved = db.getByName('GOOGL')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.body.extract().longName, 'Alphabet Inc.')


class TestDbSQLModel(unittest.TestCase):
    """
    Tests for DbSQLModel - SQLite-backed persistence without context manager.
    
    Each test gets a fresh in-memory database. All operations are organized
    by HTTP-like methods: GET, POST, DELETE, PUT.
    """

    def setUp(self):
        """Create a fresh in-memory database for each test."""
        self.db = DbSQLModel()

    # ========================================================================
    # GET Operations (Read)
    # ========================================================================
    
    def test_get_by_name(self):
        """GET: Retrieve a record by name."""
        # Setup
        aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
        self.db.post(aapl, name='AAPL')
        
        # Test
        result = self.db.getByName('AAPL')
        self.assertIsNotNone(result)
        self.assertEqual(result.info.name, 'AAPL')
        
        # Verify data integrity
        pydantic_record = result.asModel()
        ticker = pydantic_record.body.extract()
        self.assertIsInstance(ticker, Ticker)
        self.assertEqual(ticker.symbol, 'AAPL')
        self.assertEqual(ticker.longName, 'Apple Inc.')
        self.assertEqual(ticker.exchange, 'NASDAQ')

    def test_get_by_id(self):
        """GET: Retrieve a record by auto-generated ID."""
        # Setup
        googl = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
        posted = self.db.post(googl, name='GOOGL')
        record_id = posted.id
        self.assertIsNotNone(record_id)
        
        # Test
        result = self.db.getById(record_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.info.name, 'GOOGL')

    def test_get_all(self):
        """GET: Retrieve all records."""
        # Setup
        tickers = [
            Ticker(symbol='JPM',  longName='JPMorgan Chase & Co.', exchange='NYSE'),
            Ticker(symbol='BAC',  longName='Bank of America Corp', exchange='NYSE'),
            Ticker(symbol='WFC',  longName='Wells Fargo & Company', exchange='NYSE'),
        ]
        for t in tickers:
            self.db.post(t, name=t.symbol)
        
        # Test
        results = self.db.getAll()
        self.assertEqual(len(results), 3)
        names = {r.info.name for r in results}
        self.assertEqual(names, {'JPM', 'BAC', 'WFC'})

    def test_get_nonexistent_returns_none(self):
        """GET: Querying for non-existent record returns None."""
        result = self.db.getByName('DOESNOTEXIST')
        self.assertIsNone(result)
        
        result = self.db.getById(99999)
        self.assertIsNone(result)

    def test_get_preserves_data_integrity(self):
        """GET: Retrieved data matches original data exactly."""
        original = Ticker(
            symbol='NVDA',
            longName='NVIDIA Corporation',
            exchange='NASDAQ'
        )
        
        # Post
        self.db.post(original, name='NVDA')
        
        # Retrieve and verify
        sql_record = self.db.getByName('NVDA')
        pydantic_record = sql_record.asModel()
        restored = pydantic_record.body.extract()
        
        self.assertEqual(restored.symbol, original.symbol)
        self.assertEqual(restored.longName, original.longName)
        self.assertEqual(restored.exchange, original.exchange)

    # ========================================================================
    # POST Operations (Create)
    # ========================================================================
    
    def test_post_creates_new_record(self):
        """POST: Create a new record."""
        ticker = Ticker(symbol='MSFT', longName='Microsoft Corp', exchange='NASDAQ')
        rec = self.db.post(ticker, name='MSFT')
        
        self.assertIsNotNone(rec)
        self.assertEqual(rec.info.name, 'MSFT')
        
        # Verify it was created
        retrieved = self.db.getByName('MSFT')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.asModel().body.extract().symbol, 'MSFT')
    
    def test_post_multiple_records(self):
        """POST: Create multiple records."""
        tickers = [
            Ticker(symbol='META', longName='Meta Platforms', exchange='NASDAQ'),
            Ticker(symbol='NFLX', longName='Netflix Inc.', exchange='NASDAQ'),
            Ticker(symbol='DIS', longName='Disney', exchange='NYSE'),
        ]
        
        for ticker in tickers:
            self.db.post(ticker, name=ticker.symbol)
        
        # Verify all created
        all_records = self.db.getAll()
        self.assertEqual(len(all_records), 3)
        names = {r.info.name for r in all_records}
        self.assertEqual(names, {'META', 'NFLX', 'DIS'})
    
    def test_post_requires_name(self):
        """POST: Requires name parameter for BaseModel."""
        ticker = Ticker(symbol='TEST', longName='Test', exchange='NYSE')
        
        with self.assertRaises(ValueError) as ctx:
            self.db.post(ticker, name=None)
        
        self.assertIn('name is required', str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx2:
            self.db.post(ticker)  # name parameter omitted
        
        self.assertIn('name is required', str(ctx2.exception))
    
    def test_post_with_infoKw(self):
        """POST: Can pass additional infoKw parameters."""
        from pyswark.core.models.info import Info
        from pyswark.core.models.body import Body
        
        ticker = Ticker(symbol='TSLA', longName='Tesla Inc.', exchange='NASDAQ')
        rec = record.Record(
            info=Info(name='TSLA'),
            body=Body(model=ticker, contents='{}')
        )
        
        # Post Record with additional infoKw
        posted_rec = self.db.post(rec, name='TSLA_CUSTOM', custom_attr='test_value')
        self.assertEqual(posted_rec.info.name, 'TSLA_CUSTOM')

    # ========================================================================
    # DELETE Operations
    # ========================================================================
    
    def test_delete_by_name(self):
        """DELETE: Remove a record by name."""
        # Setup
        tsla = Ticker(symbol='TSLA', longName='Tesla, Inc.', exchange='NASDAQ')
        self.db.post(tsla, name='TSLA')
        self.assertIsNotNone(self.db.getByName('TSLA'))
        
        # Delete
        result = self.db.deleteByName('TSLA')
        self.assertTrue(result)
        
        # Verify deleted
        self.assertIsNone(self.db.getByName('TSLA'))

    def test_delete_by_id(self):
        """DELETE: Remove a record by ID."""
        # Setup
        amzn = Ticker(symbol='AMZN', longName='Amazon.com Inc.', exchange='NASDAQ')
        posted = self.db.post(amzn, name='AMZN')
        record_id = posted.id
        self.assertIsNotNone(self.db.getById(record_id))
        
        # Delete
        result = self.db.deleteById(record_id)
        self.assertTrue(result)
        
        # Verify deleted
        self.assertIsNone(self.db.getById(record_id))
        self.assertIsNone(self.db.getByName('AMZN'))

    def test_delete_nonexistent_returns_false(self):
        """DELETE: Deleting non-existent record returns False."""
        result = self.db.deleteByName('DOESNOTEXIST')
        self.assertFalse(result)
        
        result = self.db.deleteById(99999)
        self.assertFalse(result)

    def test_delete_preserves_other_records(self):
        """DELETE: Deleting one record doesn't affect others."""
        # Setup
        tickers = [
            Ticker(symbol='META', longName='Meta Platforms Inc.', exchange='NASDAQ'),
            Ticker(symbol='NFLX', longName='Netflix, Inc.', exchange='NASDAQ'),
            Ticker(symbol='DIS',  longName='The Walt Disney Company', exchange='NYSE'),
        ]
        for t in tickers:
            self.db.post(t, name=t.symbol)
        
        self.assertEqual(len(self.db.getAll()), 3)
        
        # Delete one
        result = self.db.deleteByName('NFLX')
        self.assertTrue(result)
        
        # Verify deleted one is gone
        self.assertIsNone(self.db.getByName('NFLX'))
        
        # Verify others still exist
        remaining = self.db.getAll()
        self.assertEqual(len(remaining), 2)
        names = {r.info.name for r in remaining}
        self.assertEqual(names, {'META', 'DIS'})

    def test_delete_and_repost(self):
        """DELETE: Can repost with same name after deletion."""
        # Setup
        original = Ticker(symbol='UBER', longName='Uber Technologies Inc.', exchange='NYSE')
        self.db.post(original, name='UBER')
        
        # Delete
        self.assertTrue(self.db.deleteByName('UBER'))
        self.assertIsNone(self.db.getByName('UBER'))
        
        # Repost with same name
        updated = Ticker(symbol='UBER', longName='Uber Technologies, Inc.', exchange='NYSE')
        self.db.post(updated, name='UBER')
        
        # Verify new record exists
        result = self.db.getByName('UBER')
        self.assertIsNotNone(result)
        self.assertEqual(result.asModel().body.extract().longName, 'Uber Technologies, Inc.')

    def test_delete_by_id_after_get_by_name(self):
        """DELETE: Delete by ID after retrieving by name."""
        # Setup
        sq = Ticker(symbol='SQ', longName='Block, Inc.', exchange='NYSE')
        self.db.post(sq, name='SQ')
        
        # Get ID from name
        record = self.db.getByName('SQ')
        record_id = record.id
        
        # Delete by ID
        result = self.db.deleteById(record_id)
        self.assertTrue(result)
        
        # Verify deleted
        self.assertIsNone(self.db.getByName('SQ'))
        self.assertIsNone(self.db.getById(record_id))

    # ========================================================================
    # PUT Operations (Update/Create)
    # ========================================================================
    
    def test_put_creates_new_record(self):
        """PUT: Creates new record when it doesn't exist."""
        aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
        sql_rec = self.db.put(aapl, name='AAPL')
        
        self.assertIsNotNone(sql_rec)
        self.assertEqual(sql_rec.info.name, 'AAPL')
        
        # Verify created
        retrieved = self.db.getByName('AAPL')
        self.assertIsNotNone(retrieved)
        ticker = retrieved.asModel().body.extract()
        self.assertEqual(ticker.symbol, 'AAPL')
        self.assertEqual(ticker.longName, 'Apple Inc.')

    def test_put_updates_existing_record(self):
        """PUT: Updates existing record by replacing it."""
        # Setup
        original = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
        self.db.post(original, name='MSFT')
        self.assertEqual(
            self.db.getByName('MSFT').asModel().body.extract().longName,
            'Microsoft Corporation'
        )
        
        # Update with PUT
        updated = Ticker(symbol='MSFT', longName='Microsoft Corp.', exchange='NASDAQ')
        self.db.put(updated, name='MSFT')
        
        # Verify updated
        retrieved = self.db.getByName('MSFT')
        self.assertIsNotNone(retrieved)
        ticker = retrieved.asModel().body.extract()
        self.assertEqual(ticker.longName, 'Microsoft Corp.')  # Updated
        self.assertEqual(ticker.symbol, 'MSFT')  # Same

    def test_put_is_idempotent(self):
        """PUT: Multiple calls with same data produce same result."""
        ticker = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
        
        # PUT multiple times
        self.db.put(ticker, name='GOOGL')
        self.db.put(ticker, name='GOOGL')
        self.db.put(ticker, name='GOOGL')
        
        # Should still have exactly one record
        retrieved = self.db.getByName('GOOGL')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.asModel().body.extract().longName, 'Alphabet Inc.')
        
        all_records = self.db.getAll()
        googl_records = [r for r in all_records if r.info.name == 'GOOGL']
        self.assertEqual(len(googl_records), 1)

    def test_put_preserves_other_records(self):
        """PUT: Only affects specified record, leaving others unchanged."""
        # Setup
        tickers = [
            Ticker(symbol='META', longName='Meta Platforms Inc.', exchange='NASDAQ'),
            Ticker(symbol='NFLX', longName='Netflix, Inc.', exchange='NASDAQ'),
            Ticker(symbol='DIS',  longName='The Walt Disney Company', exchange='NYSE'),
        ]
        for t in tickers:
            self.db.post(t, name=t.symbol)
        
        self.assertEqual(len(self.db.getAll()), 3)
        
        # PUT update to one record
        updated_nflx = Ticker(symbol='NFLX', longName='Netflix Inc.', exchange='NASDAQ')
        self.db.put(updated_nflx, name='NFLX')
        
        # Verify updated record changed
        nflx = self.db.getByName('NFLX')
        self.assertEqual(nflx.asModel().body.extract().longName, 'Netflix Inc.')
        
        # Verify other records unchanged
        meta = self.db.getByName('META')
        self.assertEqual(meta.asModel().body.extract().longName, 'Meta Platforms Inc.')
        
        dis = self.db.getByName('DIS')
        self.assertEqual(dis.asModel().body.extract().longName, 'The Walt Disney Company')
        
        # Verify still have 3 records
        self.assertEqual(len(self.db.getAll()), 3)

    def test_put_atomic_transaction(self):
        """PUT: Uses single transaction for delete and post."""
        # Setup
        original = Ticker(symbol='TEST', longName='Original Name', exchange='NASDAQ')
        self.db.post(original, name='TEST')
        self.assertEqual(
            self.db.getByName('TEST').asModel().body.extract().longName,
            'Original Name'
        )
        
        # PUT update
        updated = Ticker(symbol='TEST', longName='Updated Name', exchange='NASDAQ')
        result = self.db.put(updated, name='TEST')
        self.assertIsNotNone(result)
        
        # Verify updated
        retrieved_after = self.db.getByName('TEST')
        self.assertIsNotNone(retrieved_after)
        self.assertEqual(
            retrieved_after.asModel().body.extract().longName,
            'Updated Name'
        )
        
        # Verify only one record exists
        all_records = self.db.getAll()
        test_records = [r for r in all_records if r.info.name == 'TEST']
        self.assertEqual(len(test_records), 1)


class TestDbSQLModelConnect(unittest.TestCase):
    """
    Tests for DbSQLModel.connect() - context manager pattern for database connections.
    
    These tests verify that .connect() works as a context manager with file-based
    persistence. All operations are organized by HTTP-like methods: GET, POST, DELETE, PUT.
    """
    
    def setUp(self):
        """Set up test fixtures for file-based database."""
        import tempfile
        import os
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db_url = f'sqlite:///{self.db_path}'
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        import os
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    # ========================================================================
    # GET Operations (Read)
    # ========================================================================
    
    def test_get_by_name(self):
        """GET: Retrieve a record by name."""
        # Setup - create record in one context
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
            db.post(ticker, name='AAPL')
        
        # Test - retrieve in another context
        with DbSQLModel.connect(self.db_url) as db:
            result = db.getByName('AAPL')
            self.assertIsNotNone(result)
            self.assertEqual(result.info.name, 'AAPL')
            
            ticker = result.asModel().body.extract()
            self.assertIsInstance(ticker, Ticker)
            self.assertEqual(ticker.symbol, 'AAPL')
            self.assertEqual(ticker.longName, 'Apple Inc.')
    
    def test_get_by_id(self):
        """GET: Retrieve a record by auto-generated ID."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
            posted = db.post(ticker, name='GOOGL')
            self.record_id = posted.id
        
        # Test
        with DbSQLModel.connect(self.db_url) as db:
            result = db.getById(self.record_id)
            self.assertIsNotNone(result)
            self.assertEqual(result.info.name, 'GOOGL')
    
    def test_get_all(self):
        """GET: Retrieve all records."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            tickers = [
                Ticker(symbol='JPM', longName='JPMorgan Chase', exchange='NYSE'),
                Ticker(symbol='BAC', longName='Bank of America', exchange='NYSE'),
                Ticker(symbol='WFC', longName='Wells Fargo', exchange='NYSE'),
            ]
            for t in tickers:
                db.post(t, name=t.symbol)
        
        # Test
        with DbSQLModel.connect(self.db_url) as db:
            results = db.getAll()
            self.assertEqual(len(results), 3)
            names = {r.info.name for r in results}
            self.assertEqual(names, {'JPM', 'BAC', 'WFC'})
    
    def test_get_nonexistent_returns_none(self):
        """GET: Querying for non-existent record returns None."""
        with DbSQLModel.connect(self.db_url) as db:
            result = db.getByName('DOESNOTEXIST')
            self.assertIsNone(result)
            
            result = db.getById(99999)
            self.assertIsNone(result)
    
    def test_get_preserves_data_integrity(self):
        """GET: Retrieved data matches original data exactly."""
        original = Ticker(
            symbol='NVDA',
            longName='NVIDIA Corporation',
            exchange='NASDAQ'
        )
        
        # Post
        with DbSQLModel.connect(self.db_url) as db:
            db.post(original, name='NVDA')
        
        # Retrieve and verify
        with DbSQLModel.connect(self.db_url) as db:
            sql_record = db.getByName('NVDA')
            pydantic_record = sql_record.asModel()
            restored = pydantic_record.body.extract()
            
            self.assertEqual(restored.symbol, original.symbol)
            self.assertEqual(restored.longName, original.longName)
            self.assertEqual(restored.exchange, original.exchange)
    
    # ========================================================================
    # POST Operations (Create)
    # ========================================================================
    
    def test_post_creates_new_record(self):
        """POST: Create a new record."""
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='MSFT', longName='Microsoft Corp', exchange='NASDAQ')
            rec = db.post(ticker, name='MSFT')
            
            self.assertIsNotNone(rec)
            self.assertEqual(rec.info.name, 'MSFT')
            
            # Verify it was created
            retrieved = db.getByName('MSFT')
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.asModel().body.extract().symbol, 'MSFT')
    
    def test_post_auto_commits_on_success(self):
        """POST: Auto-commits on successful context exit."""
        # Post in context
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
            db.post(ticker, name='GOOGL')
            # No explicit commit - should auto-commit on exit
        
        # Verify data persisted in new context
        with DbSQLModel.connect(self.db_url) as db:
            retrieved = db.getByName('GOOGL')
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.asModel().body.extract().symbol, 'GOOGL')
    
    def test_post_rolls_back_on_exception(self):
        """POST: Rolls back on exception."""
        # Try to post but raise exception
        try:
            with DbSQLModel.connect(self.db_url) as db:
                ticker = Ticker(symbol='TSLA', longName='Tesla Inc.', exchange='NASDAQ')
                db.post(ticker, name='TSLA')
                raise ValueError("Simulated error")
        except ValueError:
            pass  # Expected
        
        # Verify data was NOT persisted (rolled back)
        with DbSQLModel.connect(self.db_url) as db:
            retrieved = db.getByName('TSLA')
            self.assertIsNone(retrieved)
    
    def test_post_multiple_records(self):
        """POST: Create multiple records in single transaction."""
        with DbSQLModel.connect(self.db_url) as db:
            tickers = [
                Ticker(symbol='META', longName='Meta Platforms', exchange='NASDAQ'),
                Ticker(symbol='NFLX', longName='Netflix Inc.', exchange='NASDAQ'),
                Ticker(symbol='DIS', longName='Disney', exchange='NYSE'),
            ]
            
            for ticker in tickers:
                db.post(ticker, name=ticker.symbol)
        
        # Verify all persisted
        with DbSQLModel.connect(self.db_url) as db:
            all_records = db.getAll()
            self.assertEqual(len(all_records), 3)
            names = {r.info.name for r in all_records}
            self.assertEqual(names, {'META', 'NFLX', 'DIS'})
    
    def test_post_all_in_context_manager(self):
        """POST: postAll() works within context manager and auto-commits."""
        from pyswark.core.models import info
        
        # Test postAll() within context manager (covers lines 294-301)
        with DbSQLModel.connect(self.db_url) as db:
            tickers = [
                Ticker(symbol='JPM', longName='JPMorgan Chase', exchange='NYSE'),
                Ticker(symbol='BAC', longName='Bank of America', exchange='NYSE'),
                Ticker(symbol='WFC', longName='Wells Fargo', exchange='NYSE'),
            ]
            
            # Create Records with names for postAll()
            records = [
                record.Record(
                    info=info.Info(name=ticker.symbol),
                    body=body.Body(model=ticker)
                )
                for ticker in tickers
            ]
            
            # Use postAll() instead of individual post() calls
            sql_models = db.postAll(records)
            
            # Verify models were returned
            self.assertEqual(len(sql_models), 3)
            self.assertTrue(all(hasattr(m, 'id') for m in sql_models))
            
            # Verify all have IDs (flushed and refreshed)
            ids = {m.id for m in sql_models}
            self.assertEqual(len(ids), 3)
            self.assertTrue(all(id is not None for id in ids))
        
        # Verify all persisted after context exit (auto-commit worked)
        with DbSQLModel.connect(self.db_url) as db:
            all_records = db.getAll()
            self.assertEqual(len(all_records), 3)
            names = {r.info.name for r in all_records}
            self.assertEqual(names, {'JPM', 'BAC', 'WFC'})
            
            # Verify individual records can be retrieved
            jpm = db.getByName('JPM')
            self.assertIsNotNone(jpm)
            self.assertEqual(jpm.asModel().body.extract().symbol, 'JPM')
    
    def test_post_requires_name(self):
        """POST: Requires name parameter for BaseModel."""
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='TEST', longName='Test', exchange='NYSE')
            
            with self.assertRaises(ValueError) as ctx:
                db.post(ticker, name=None)
            
            self.assertIn('name is required', str(ctx.exception))
    
    # ========================================================================
    # DELETE Operations
    # ========================================================================
    
    def test_delete_by_name(self):
        """DELETE: Remove a record by name."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='TSLA', longName='Tesla Inc.', exchange='NASDAQ')
            db.post(ticker, name='TSLA')
        
        # Delete
        with DbSQLModel.connect(self.db_url) as db:
            result = db.deleteByName('TSLA')
            self.assertTrue(result)
        
        # Verify deleted
        with DbSQLModel.connect(self.db_url) as db:
            self.assertIsNone(db.getByName('TSLA'))
    
    def test_delete_by_id(self):
        """DELETE: Remove a record by ID."""
        # Setup
        record_id = None
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='AMZN', longName='Amazon Inc.', exchange='NASDAQ')
            posted = db.post(ticker, name='AMZN')
            record_id = posted.id
        
        # Delete
        with DbSQLModel.connect(self.db_url) as db:
            result = db.deleteById(record_id)
            self.assertTrue(result)
        
        # Verify deleted
        with DbSQLModel.connect(self.db_url) as db:
            self.assertIsNone(db.getById(record_id))
            self.assertIsNone(db.getByName('AMZN'))
    
    def test_delete_nonexistent_returns_false(self):
        """DELETE: Deleting non-existent record returns False."""
        with DbSQLModel.connect(self.db_url) as db:
            result = db.deleteByName('DOESNOTEXIST')
            self.assertFalse(result)
            
            result = db.deleteById(99999)
            self.assertFalse(result)
    
    def test_delete_preserves_other_records(self):
        """DELETE: Deleting one record doesn't affect others."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            tickers = [
                Ticker(symbol='META', longName='Meta Platforms', exchange='NASDAQ'),
                Ticker(symbol='NFLX', longName='Netflix Inc.', exchange='NASDAQ'),
                Ticker(symbol='DIS', longName='Disney', exchange='NYSE'),
            ]
            for t in tickers:
                db.post(t, name=t.symbol)
        
        # Delete one
        with DbSQLModel.connect(self.db_url) as db:
            result = db.deleteByName('NFLX')
            self.assertTrue(result)
        
        # Verify others still exist
        with DbSQLModel.connect(self.db_url) as db:
            self.assertIsNone(db.getByName('NFLX'))
            self.assertIsNotNone(db.getByName('META'))
            self.assertIsNotNone(db.getByName('DIS'))
    
    def test_delete_and_repost(self):
        """DELETE: Can repost with same name after deletion."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            original = Ticker(symbol='UBER', longName='Uber Technologies', exchange='NYSE')
            db.post(original, name='UBER')
        
        # Delete
        with DbSQLModel.connect(self.db_url) as db:
            self.assertTrue(db.deleteByName('UBER'))
        
        # Repost with same name
        with DbSQLModel.connect(self.db_url) as db:
            updated = Ticker(symbol='UBER', longName='Uber Technologies Inc.', exchange='NYSE')
            db.post(updated, name='UBER')
        
        # Verify new record exists
        with DbSQLModel.connect(self.db_url) as db:
            result = db.getByName('UBER')
            self.assertIsNotNone(result)
            self.assertEqual(
                result.asModel().body.extract().longName,
                'Uber Technologies Inc.'
            )
    
    # ========================================================================
    # PUT Operations (Update/Create)
    # ========================================================================
    
    def test_put_creates_new_record(self):
        """PUT: Creates new record when it doesn't exist."""
        with DbSQLModel.connect(self.db_url) as db:
            ticker = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
            sql_rec = db.put(ticker, name='AAPL')
            
            self.assertIsNotNone(sql_rec)
            self.assertEqual(sql_rec.info.name, 'AAPL')
        
        # Verify persisted
        with DbSQLModel.connect(self.db_url) as db:
            retrieved = db.getByName('AAPL')
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.asModel().body.extract().symbol, 'AAPL')
    
    def test_put_updates_existing_record(self):
        """PUT: Updates existing record by replacing it."""
        # Create initial record
        with DbSQLModel.connect(self.db_url) as db:
            original = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
            db.post(original, name='MSFT')
        
        # Update with PUT
        with DbSQLModel.connect(self.db_url) as db:
            updated = Ticker(symbol='MSFT', longName='Microsoft Corp.', exchange='NASDAQ')
            db.put(updated, name='MSFT')
        
        # Verify updated
        with DbSQLModel.connect(self.db_url) as db:
            retrieved = db.getByName('MSFT')
            ticker = retrieved.asModel().body.extract()
            self.assertEqual(ticker.longName, 'Microsoft Corp.')  # Updated
            self.assertEqual(ticker.symbol, 'MSFT')  # Same
    
    def test_put_is_idempotent(self):
        """PUT: Multiple calls with same data produce same result."""
        ticker = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
        
        # PUT multiple times
        with DbSQLModel.connect(self.db_url) as db:
            db.put(ticker, name='GOOGL')
        
        with DbSQLModel.connect(self.db_url) as db:
            db.put(ticker, name='GOOGL')
        
        with DbSQLModel.connect(self.db_url) as db:
            db.put(ticker, name='GOOGL')
        
        # Should still have exactly one record
        with DbSQLModel.connect(self.db_url) as db:
            all_records = db.getAll()
            googl_records = [r for r in all_records if r.info.name == 'GOOGL']
            self.assertEqual(len(googl_records), 1)
    
    def test_put_preserves_other_records(self):
        """PUT: Only affects specified record, leaving others unchanged."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            tickers = [
                Ticker(symbol='META', longName='Meta Platforms Inc.', exchange='NASDAQ'),
                Ticker(symbol='NFLX', longName='Netflix, Inc.', exchange='NASDAQ'),
                Ticker(symbol='DIS', longName='The Walt Disney Company', exchange='NYSE'),
            ]
            for t in tickers:
                db.post(t, name=t.symbol)
        
        # PUT update to one record
        with DbSQLModel.connect(self.db_url) as db:
            updated_nflx = Ticker(symbol='NFLX', longName='Netflix Inc.', exchange='NASDAQ')
            db.put(updated_nflx, name='NFLX')
        
        # Verify the updated record changed
        with DbSQLModel.connect(self.db_url) as db:
            nflx = db.getByName('NFLX')
            self.assertEqual(nflx.asModel().body.extract().longName, 'Netflix Inc.')
            
            # Verify other records unchanged
            meta = db.getByName('META')
            self.assertEqual(meta.asModel().body.extract().longName, 'Meta Platforms Inc.')
            
            dis = db.getByName('DIS')
            self.assertEqual(dis.asModel().body.extract().longName, 'The Walt Disney Company')
            
            # Verify still have 3 records
            self.assertEqual(len(db.getAll()), 3)
    
    def test_put_atomic_transaction(self):
        """PUT: Uses single transaction for delete and post."""
        # Setup
        with DbSQLModel.connect(self.db_url) as db:
            original = Ticker(symbol='TEST', longName='Original Name', exchange='NASDAQ')
            db.post(original, name='TEST')
        
        # PUT update
        with DbSQLModel.connect(self.db_url) as db:
            updated = Ticker(symbol='TEST', longName='Updated Name', exchange='NASDAQ')
            result = db.put(updated, name='TEST')
            self.assertIsNotNone(result)
        
        # Verify updated
        with DbSQLModel.connect(self.db_url) as db:
            retrieved = db.getByName('TEST')
            self.assertEqual(
                retrieved.asModel().body.extract().longName,
                'Updated Name'
            )
            
            # Verify only one record exists
            all_records = db.getAll()
            test_records = [r for r in all_records if r.info.name == 'TEST']
            self.assertEqual(len(test_records), 1)
    
    # ========================================================================
    # Edge Cases: Commit/Rollback
    # ========================================================================
    
    def test_commit_rollback_edge_cases(self):
        """
        Test edge cases for commit() and rollback() methods and exception handling.
        
        Covers:
        - commit() called outside context manager raises RuntimeError
        - rollback() called outside context manager raises RuntimeError
        - put() exception handling in context manager triggers rollback
        - put() exception handling outside context manager triggers rollback
        """
        # Test 1: commit() outside context manager raises RuntimeError
        db = DbSQLModel.connect(self.db_url)
        with self.assertRaises(RuntimeError) as ctx:
            db.commit()
        self.assertIn("context manager", str(ctx.exception).lower())
        
        # Test 2: rollback() outside context manager raises RuntimeError
        db = DbSQLModel.connect(self.db_url)
        with self.assertRaises(RuntimeError) as ctx:
            db.rollback()
        self.assertIn("context manager", str(ctx.exception).lower())
        
        # Test 3: put() exception handling in context manager triggers rollback
        # Setup - create initial record
        with DbSQLModel.connect(self.db_url) as db:
            original = Ticker(symbol='ERROR_TEST', longName='Original', exchange='NASDAQ')
            db.post(original, name='ERROR_TEST')
        
        # Verify it exists
        with DbSQLModel.connect(self.db_url) as db:
            self.assertIsNotNone(db.getByName('ERROR_TEST'))
        
        # Simulate exception during put() in context manager
        from unittest.mock import patch, MagicMock
        from sqlmodel import Session
        
        # Mock Session.add to raise an exception
        with patch.object(Session, 'add', side_effect=Exception("Simulated put error")):
            try:
                with DbSQLModel.connect(self.db_url) as db:
                    updated = Ticker(symbol='ERROR_TEST', longName='Should Fail', exchange='NASDAQ')
                    db.put(updated, name='ERROR_TEST')
            except Exception as e:
                self.assertIn("Simulated put error", str(e))
        
        # Verify original record still exists (rollback worked)
        with DbSQLModel.connect(self.db_url) as db:
            retrieved = db.getByName('ERROR_TEST')
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.asModel().body.extract().longName, 'Original')
        
        # Test 4: put() exception handling outside context manager triggers rollback
        # Setup - create initial record
        db = DbSQLModel(self.db_url)
        original2 = Ticker(symbol='ERROR_TEST2', longName='Original2', exchange='NASDAQ')
        db.post(original2, name='ERROR_TEST2')
        
        # Verify it exists
        self.assertIsNotNone(db.getByName('ERROR_TEST2'))
        
        # Mock Session.add to raise an exception (non-context manager path)
        # This tests the exception handling in put() when not using context manager
        with patch.object(Session, 'add', side_effect=Exception("Simulated put error 2")):
            db2 = DbSQLModel(self.db_url)
            updated2 = Ticker(symbol='ERROR_TEST2', longName='Should Fail', exchange='NASDAQ')
            with self.assertRaises(Exception) as ctx:
                db2.put(updated2, name='ERROR_TEST2')
            self.assertIn("Simulated put error 2", str(ctx.exception))
        
        # Verify original record still exists and unchanged (rollback prevented update)
        db3 = DbSQLModel(self.db_url)
        retrieved2 = db3.getByName('ERROR_TEST2')
        self.assertIsNotNone(retrieved2)
        self.assertEqual(retrieved2.asModel().body.extract().longName, 'Original2')


if __name__ == '__main__':
    unittest.main()
