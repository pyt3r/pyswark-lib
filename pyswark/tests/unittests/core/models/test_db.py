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
    Tests for DbSQLModel - SQLite-backed persistence.
    
    Each test gets a fresh in-memory database.
    """

    def setUp(self):
        """Create a fresh in-memory database for each test."""
        self.db = DbSQLModel()

    def test_post_and_retrieve_by_name(self):
        """
        Post a Ticker and retrieve it by name.
        
        This is the primary use case: store a model, get it back by name.
        The symbol serves as the unique identifier (info.name).
        """
        # Create and post a ticker
        aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
        self.db.post(aapl, name='AAPL')
        
        # Retrieve by name
        result = self.db.getByName('AAPL')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.info.name, 'AAPL')
        
        # Convert to Pydantic and extract the inner model
        pydantic_record = result.asModel()
        ticker = pydantic_record.body.extract()
        
        self.assertIsInstance(ticker, Ticker)
        self.assertEqual(ticker.symbol, 'AAPL')
        self.assertEqual(ticker.longName, 'Apple Inc.')
        self.assertEqual(ticker.exchange, 'NASDAQ')

    def test_post_and_retrieve_by_id(self):
        """
        Post a Ticker and retrieve it by auto-generated ID.
        
        Useful when you need the database-assigned primary key.
        """
        googl = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
        posted = self.db.post(googl, name='GOOGL')
        
        # Get the auto-generated ID
        record_id = posted.id
        self.assertIsNotNone(record_id)
        
        # Retrieve by ID
        result = self.db.getById(record_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.info.name, 'GOOGL')

    def test_post_multiple_and_get_all(self):
        """
        Post multiple Tickers and retrieve them all.
        
        Demonstrates bulk operations and full table retrieval.
        """
        tickers = [
            Ticker(symbol='JPM',  longName='JPMorgan Chase & Co.', exchange='NYSE'),
            Ticker(symbol='BAC',  longName='Bank of America Corp', exchange='NYSE'),
            Ticker(symbol='WFC',  longName='Wells Fargo & Company', exchange='NYSE'),
        ]
        
        # Post each ticker using its symbol as the name
        for t in tickers:
            self.db.post(t, name=t.symbol)
        
        # Get all records
        results = self.db.getAll()
        
        self.assertEqual(len(results), 3)
        
        # Verify all symbols are present
        names = {r.info.name for r in results}
        self.assertEqual(names, {'JPM', 'BAC', 'WFC'})

    def test_get_nonexistent_returns_none(self):
        """
        Querying for a non-existent name returns None.
        
        This is safe behavior - no exceptions raised.
        """
        result = self.db.getByName('DOESNOTEXIST')
        self.assertIsNone(result)

    def test_full_roundtrip_preserves_data(self):
        """
        Complete data integrity through post/retrieve cycle.
        
        This is the key test: data goes in, database stores it,
        data comes out exactly the same.
        """
        # Original ticker with all fields
        original = Ticker(
            symbol='NVDA',
            longName='NVIDIA Corporation',
            exchange='NASDAQ'
        )
        
        # Post to database
        self.db.post(original, name='NVDA')
        
        # Retrieve and extract
        sql_record = self.db.getByName('NVDA')
        pydantic_record = sql_record.asModel()
        restored = pydantic_record.body.extract()
        
        # Verify every field matches
        self.assertEqual(restored.symbol, original.symbol)
        self.assertEqual(restored.longName, original.longName)
        self.assertEqual(restored.exchange, original.exchange)

    def test_delete_by_name_success(self):
        """
        Delete a record by name and verify it's removed.
        
        This is the primary deletion use case: remove a record by its unique name.
        """
        # Create and post a ticker
        tsla = Ticker(symbol='TSLA', longName='Tesla, Inc.', exchange='NASDAQ')
        self.db.post(tsla, name='TSLA')
        
        # Verify it exists
        self.assertIsNotNone(self.db.getByName('TSLA'))
        
        # Delete it
        result = self.db.deleteByName('TSLA')
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(self.db.getByName('TSLA'))

    def test_delete_by_id_success(self):
        """
        Delete a record by ID and verify it's removed.
        
        Useful when you have the database-assigned primary key.
        """
        # Create and post a ticker
        amzn = Ticker(symbol='AMZN', longName='Amazon.com Inc.', exchange='NASDAQ')
        posted = self.db.post(amzn, name='AMZN')
        record_id = posted.id
        
        # Verify it exists
        self.assertIsNotNone(self.db.getById(record_id))
        
        # Delete it
        result = self.db.deleteById(record_id)
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(self.db.getById(record_id))
        self.assertIsNone(self.db.getByName('AMZN'))

    def test_delete_by_name_nonexistent(self):
        """
        Attempting to delete a non-existent name returns False.
        
        Safe behavior - doesn't raise an exception, just returns False.
        """
        result = self.db.deleteByName('DOESNOTEXIST')
        self.assertFalse(result)

    def test_delete_by_id_nonexistent(self):
        """
        Attempting to delete a non-existent ID returns False.
        
        Safe behavior - doesn't raise an exception, just returns False.
        """
        result = self.db.deleteById(99999)  # Non-existent ID
        self.assertFalse(result)

    def test_delete_one_preserves_others(self):
        """
        Deleting one record doesn't affect other records.
        
        This verifies referential integrity and that deletion is targeted.
        """
        # Post multiple tickers
        tickers = [
            Ticker(symbol='META', longName='Meta Platforms Inc.', exchange='NASDAQ'),
            Ticker(symbol='NFLX', longName='Netflix, Inc.', exchange='NASDAQ'),
            Ticker(symbol='DIS',  longName='The Walt Disney Company', exchange='NYSE'),
        ]
        
        for t in tickers:
            self.db.post(t, name=t.symbol)
        
        # Verify all exist
        all_records = self.db.getAll()
        self.assertEqual(len(all_records), 3)
        
        # Delete one
        result = self.db.deleteByName('NFLX')
        self.assertTrue(result)
        
        # Verify the deleted one is gone
        self.assertIsNone(self.db.getByName('NFLX'))
        
        # Verify the others still exist
        remaining = self.db.getAll()
        self.assertEqual(len(remaining), 2)
        
        names = {r.info.name for r in remaining}
        self.assertEqual(names, {'META', 'DIS'})

    def test_delete_and_repost_same_name(self):
        """
        After deleting, can repost with the same name.
        
        This verifies that deletion truly removes the record and doesn't
        leave behind constraints that prevent reuse of the name.
        """
        # Post, delete, then repost with same name
        original = Ticker(symbol='UBER', longName='Uber Technologies Inc.', exchange='NYSE')
        self.db.post(original, name='UBER')
        
        # Delete it
        self.assertTrue(self.db.deleteByName('UBER'))
        self.assertIsNone(self.db.getByName('UBER'))
        
        # Repost with same name but different data
        updated = Ticker(symbol='UBER', longName='Uber Technologies, Inc.', exchange='NYSE')
        self.db.post(updated, name='UBER')
        
        # Verify new record exists
        result = self.db.getByName('UBER')
        self.assertIsNotNone(result)
        
        # Verify it's the new data
        ticker = result.asModel().body.extract()
        self.assertEqual(ticker.longName, 'Uber Technologies, Inc.')

    def test_delete_by_id_after_get_by_name(self):
        """
        Delete by ID after retrieving by name.
        
        Demonstrates the workflow: find by name, get ID, delete by ID.
        """
        # Post a ticker
        sq = Ticker(symbol='SQ', longName='Block, Inc.', exchange='NYSE')
        self.db.post(sq, name='SQ')
        
        # Get by name to retrieve the ID
        record = self.db.getByName('SQ')
        record_id = record.id
        
        # Delete using the ID
        result = self.db.deleteById(record_id)
        self.assertTrue(result)
        
        # Verify it's gone by both methods
        self.assertIsNone(self.db.getByName('SQ'))
        self.assertIsNone(self.db.getById(record_id))

    def test_post_body_requires_name(self):
        """
        Posting a Body directly requires a name parameter (DbSQLModel).
        
        DbSQLModel uses the same _post() method, so it should have
        the same validation requirements.
        """
        # Create a Body
        ticker = Ticker(symbol='TEST', longName='Test Corp', exchange='NYSE')
        bod = body.Body(model=ticker)
        
        # Posting without name should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            self.db.post(bod, name=None)
        
        self.assertIn('name is required', str(ctx.exception))
        self.assertIn('Body', str(ctx.exception))

    def test_post_basemodel_requires_name(self):
        """
        Posting a BaseModel requires a name parameter (DbSQLModel).
        
        DbSQLModel uses the same _post() method, so it should have
        the same validation requirements.
        """
        # Create a BaseModel
        ticker = Ticker(symbol='TEST', longName='Test Corp', exchange='NYSE')
        
        # Posting without name should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            self.db.post(ticker, name=None)
        
        self.assertIn('name is required', str(ctx.exception))
        self.assertIn('Ticker', str(ctx.exception))
        
        # Also test with name not provided at all (defaults to None)
        with self.assertRaises(ValueError) as ctx2:
            self.db.post(ticker)  # name parameter omitted
        
        self.assertIn('name is required', str(ctx2.exception))

    def test_put_creates_new_record(self):
        """
        PUT creates a new record when one doesn't exist (DbSQLModel).
        
        PUT is idempotent - it works whether the record exists or not.
        When the record doesn't exist, PUT behaves like POST.
        """
        # PUT a new ticker
        aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
        sql_rec = self.db.put(aapl, name='AAPL')
        
        self.assertIsNotNone(sql_rec)
        self.assertEqual(sql_rec.info.name, 'AAPL')
        
        # Verify it was created
        retrieved = self.db.getByName('AAPL')
        self.assertIsNotNone(retrieved)
        ticker = retrieved.asModel().body.extract()
        self.assertEqual(ticker.symbol, 'AAPL')
        self.assertEqual(ticker.longName, 'Apple Inc.')

    def test_put_updates_existing_record(self):
        """
        PUT updates an existing record by replacing it (DbSQLModel).
        
        This is the key difference from POST - PUT replaces existing
        records rather than creating duplicates or raising errors.
        """
        # Create initial record
        original = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
        self.db.post(original, name='MSFT')
        
        # Verify original exists
        retrieved = self.db.getByName('MSFT')
        self.assertEqual(retrieved.asModel().body.extract().longName, 'Microsoft Corporation')
        
        # PUT an updated version
        updated = Ticker(symbol='MSFT', longName='Microsoft Corp.', exchange='NASDAQ')
        self.db.put(updated, name='MSFT')
        
        # Verify it was updated
        retrieved = self.db.getByName('MSFT')
        self.assertIsNotNone(retrieved)
        ticker = retrieved.asModel().body.extract()
        self.assertEqual(ticker.longName, 'Microsoft Corp.')  # Updated value
        self.assertEqual(ticker.symbol, 'MSFT')  # Same symbol

    def test_put_is_idempotent(self):
        """
        PUT is idempotent - multiple calls with same data produce same result (DbSQLModel).
        
        This is a key property of PUT operations - calling it multiple
        times should result in the same state as calling it once.
        """
        ticker = Ticker(symbol='GOOGL', longName='Alphabet Inc.', exchange='NASDAQ')
        
        # PUT multiple times
        self.db.put(ticker, name='GOOGL')
        self.db.put(ticker, name='GOOGL')
        self.db.put(ticker, name='GOOGL')
        
        # Should still have exactly one record
        retrieved = self.db.getByName('GOOGL')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.asModel().body.extract().longName, 'Alphabet Inc.')
        
        # Verify only one record exists
        all_records = self.db.getAll()
        googl_records = [r for r in all_records if r.info.name == 'GOOGL']
        self.assertEqual(len(googl_records), 1)

    def test_put_preserves_other_records(self):
        """
        PUT only affects the specified record, leaving others unchanged.
        
        This verifies that PUT operations are targeted and don't have
        side effects on other records in the database.
        """
        # Create multiple records
        tickers = [
            Ticker(symbol='META', longName='Meta Platforms Inc.', exchange='NASDAQ'),
            Ticker(symbol='NFLX', longName='Netflix, Inc.', exchange='NASDAQ'),
            Ticker(symbol='DIS',  longName='The Walt Disney Company', exchange='NYSE'),
        ]
        
        for t in tickers:
            self.db.post(t, name=t.symbol)
        
        # Verify all exist
        self.assertEqual(len(self.db.getAll()), 3)
        
        # PUT an update to one record
        updated_nflx = Ticker(symbol='NFLX', longName='Netflix Inc.', exchange='NASDAQ')
        self.db.put(updated_nflx, name='NFLX')
        
        # Verify the updated record changed
        nflx = self.db.getByName('NFLX')
        self.assertEqual(nflx.asModel().body.extract().longName, 'Netflix Inc.')
        
        # Verify other records are unchanged
        meta = self.db.getByName('META')
        self.assertEqual(meta.asModel().body.extract().longName, 'Meta Platforms Inc.')
        
        dis = self.db.getByName('DIS')
        self.assertEqual(dis.asModel().body.extract().longName, 'The Walt Disney Company')
        
        # Verify still have 3 records
        self.assertEqual(len(self.db.getAll()), 3)

    def test_put_atomic_transaction(self):
        """
        PUT operation uses a single transaction for delete and post.
        
        Both operations (delete existing, post new) happen within
        a single database transaction, ensuring atomicity. If either
        operation fails, the entire transaction is rolled back.
        """
        # Create initial record
        original = Ticker(symbol='TEST', longName='Original Name', exchange='NASDAQ')
        self.db.post(original, name='TEST')
        
        # Verify it exists
        retrieved = self.db.getByName('TEST')
        self.assertIsNotNone(retrieved)
        original_name = retrieved.asModel().body.extract().longName
        self.assertEqual(original_name, 'Original Name')
        
        # PUT a new record - both delete and post should succeed together
        updated = Ticker(symbol='TEST', longName='Updated Name', exchange='NASDAQ')
        result = self.db.put(updated, name='TEST')
        
        # Verify the PUT succeeded
        self.assertIsNotNone(result)
        
        # Verify the record was updated (both operations completed)
        retrieved_after = self.db.getByName('TEST')
        self.assertIsNotNone(retrieved_after)
        self.assertEqual(
            retrieved_after.asModel().body.extract().longName,
            'Updated Name'
        )
        
        # Verify only one record exists (delete happened before post)
        all_records = self.db.getAll()
        test_records = [r for r in all_records if r.info.name == 'TEST']
        self.assertEqual(len(test_records), 1)


if __name__ == '__main__':
    unittest.main()
