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
    """Tests for the Db class (in-memory record collection)."""

    def test_post_basemodel_with_name(self):
        """
        Post a BaseModel to Db with a name.
        
        The model gets wrapped in a Record with the given name as info.name.
        """
        db = Db()
        ticker = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
        
        rec = db.post(ticker, name='MSFT')
        
        self.assertIsInstance(rec, record.Record)
        self.assertEqual(rec.info.name, 'MSFT')
        
        # Extract the original model back
        extracted = rec.body.extract()
        self.assertIsInstance(extracted, Ticker)
        self.assertEqual(extracted.symbol, 'MSFT')
        self.assertEqual(extracted.longName, 'Microsoft Corporation')


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


if __name__ == '__main__':
    unittest.main()
