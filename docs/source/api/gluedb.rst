gluedb - Data Catalogs
======================

The ``gluedb`` module provides data catalog functionality for managing
named collections of data sources. This is Layer 2 of the architecture.

Key Concepts
------------

- **GlueDb**: A database of named records pointing to data sources
- **GlueHub**: A hub containing multiple GlueDb instances
- **Record**: A named entry with URI and extraction settings


GlueDb Class
------------

.. autoclass:: pyswark.gluedb.db.Db
   :members: extract, get, delete, getNames, merge, __contains__
   :undoc-members:
   :show-inheritance:

GlueHub Class
-------------

.. autoclass:: pyswark.gluedb.hub.Hub
   :members: extract, load, getFromDb, postToDb, putToDb, deleteFromDb, extractFromDb, acquireFromDb, mergeToDb, toDb
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Connecting to an Existing GlueDb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.core.io import api

   # Connect to a .gluedb file
   db = api.read('pyswark:/data/sma-example.gluedb')

   # View available records
   print(db.getNames())  # ['JPM', 'BAC', 'kwargs']

   # Extract data by name
   jpm_data = db.extract('JPM')
   print(jpm_data.shape)

Creating a New GlueDb
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import db
   from pyswark.core.models import collection
   from pyswark.core.io import api as io

   # Create a new empty database
   db = db.Db()

   # Post records pointing to data sources
   db.post('JPM', 'pyswark:/data/ohlc-jpm.csv.gz')
   db.post('BAC', 'pyswark:/data/ohlc-bac.csv.gz')

   # Post inline data (dict, list, etc.)
   db.post('config', collection.Dict({
       'window': 60,
       'method': 'rolling'
   }))

   print(db.getNames())  # ['JPM', 'BAC', 'config']

   # Save the database
   io.write(db, 'file:./my-analysis.gluedb')

Persisting with Db.connect
^^^^^^^^^^^^^^^^^^^^^^^^^^

``Db.connect()`` loads a ``.gluedb`` catalog from a URI and returns a context
manager. When ``persist=True``, the catalog is written back to the file on
successful exit:

.. code-block:: python

   from pyswark.gluedb.db import Db
   from pyswark.core.models import collection
   from pyswark.core.io import api

   # Create an initial catalog and save it
   db = Db()
   db.post('pyswark:/data/ohlc-jpm.csv.gz', name='JPM')
   api.write(db, 'file:./catalog.gluedb')

   # Re-open with persist=True — auto-saves on exit
   with Db.connect('file:./catalog.gluedb', persist=True) as db:
       db.post(collection.Dict({'window': 60}), name='kwargs')

   # Changes are persisted
   db = Db.connect('file:./catalog.gluedb')
   print(db.getNames())  # ['JPM', 'kwargs']

   # Extract data
   jpm_data = db.extract('JPM')

Persisting with DbSQLModel.connect
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``DbSQLModel.connect()`` provides SQLite-backed persistence with automatic
commit/rollback semantics. Data posted inside a ``with`` block is committed
on successful exit and rolled back on exception:

.. code-block:: python

   from pyswark.core.models.db import DbSQLModel
   from pyswark.lib.pydantic import base

   class Ticker(base.BaseModel):
       symbol   : str
       longName : str
       exchange : str

   db_url = 'sqlite:///./my-tickers.db'

   # Post records — auto-commits on exit
   with DbSQLModel.connect(db_url) as db:
       aapl = Ticker(symbol='AAPL', longName='Apple Inc.', exchange='NASDAQ')
       db.post(aapl, name='AAPL')

       msft = Ticker(symbol='MSFT', longName='Microsoft Corp', exchange='NASDAQ')
       db.post(msft, name='MSFT')

   # Data persists across connections
   with DbSQLModel.connect(db_url) as db:
       result = db.getByName('AAPL')
       ticker = result.body.extract()
       print(ticker.symbol)    # 'AAPL'
       print(ticker.longName)  # 'Apple Inc.'

       all_records = db.getAll()
       print(len(all_records))  # 2

Updating and deleting records:

.. code-block:: python

   # PUT replaces or creates a record (idempotent)
   with DbSQLModel.connect(db_url) as db:
       updated = Ticker(symbol='MSFT', longName='Microsoft Corporation', exchange='NASDAQ')
       db.put(updated, name='MSFT')

   # DELETE removes a record
   with DbSQLModel.connect(db_url) as db:
       db.deleteByName('MSFT')

   # Verify
   with DbSQLModel.connect(db_url) as db:
       print(db.getByName('MSFT'))  # None

Rollback on exception:

.. code-block:: python

   # If an exception occurs, changes are rolled back
   try:
       with DbSQLModel.connect(db_url) as db:
           db.post(Ticker(symbol='TSLA', longName='Tesla', exchange='NASDAQ'), name='TSLA')
           raise ValueError("something went wrong")
   except ValueError:
       pass

   with DbSQLModel.connect(db_url) as db:
       print(db.getByName('TSLA'))  # None (rolled back)

Merging Databases
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import db

   db1 = db.Db()
   db1.post('data1', 'file:./data1.csv')

   db2 = db.Db()
   db2.post('data2', 'file:./data2.csv')

   # Merge db2 into db1
   db1.merge(db2)
   print(db1.getNames())  # ['data1', 'data2']

Using GlueHub for Multiple Databases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import hub

   gluedb_hub = hub.Hub()
   gluedb_hub.post('market_data', market_db)
   gluedb_hub.post('config', config_db)

   # Extract a specific database from the hub
   market_db = gluedb_hub.extract('market_data')

Per-Database Helpers
^^^^^^^^^^^^^^^^^^^^

When a hub entry points at a URI (for example, a ``.gluedb`` file), you can
modify the underlying database and persist changes back to the file using the
convenience helpers:

.. code-block:: python

   from pyswark.gluedb import hub
   from pyswark.core.models import collection

   gluedb_hub = hub.Hub()
   gluedb_hub.post('file:./catalog.gluedb', name='catalog')

   # Post a new record into the underlying GlueDb and overwrite the file
   gluedb_hub.postToDb(
       collection.Dict({'window': 120}),
       'catalog',
       name='kwargs_120',
   )

   # Merge another GlueDb and persist the merged result
   from pyswark.gluedb import db as gluedb

   other = gluedb.Db()
   other.post('extra', 'file:./extra.csv')

   gluedb_hub.mergeToDb(other, 'catalog')

