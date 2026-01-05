gluedb - Data Catalogs
======================

The ``gluedb`` module provides data catalog functionality for managing
named collections of data sources. This is Layer 2 of the architecture.

Key Concepts
------------

- **GlueDb**: A database of named records pointing to data sources
- **GlueHub**: A hub containing multiple GlueDb instances
- **Record**: A named entry with URI and extraction settings

API Functions
-------------

.. automodule:: pyswark.gluedb.api
   :members: connect, newDb, newHub
   :undoc-members:
   :show-inheritance:

GlueDb Class
------------

.. autoclass:: pyswark.gluedb.db.GlueDb
   :members: merge
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Connecting to an Existing GlueDb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import api

   # Connect to a .gluedb file
   db = api.connect('pyswark:/data/sma-example.gluedb')

   # View available records
   print(db.getNames())  # ['JPM', 'BAC', 'kwargs']

   # Extract data by name
   jpm_data = db.extract('JPM')
   print(jpm_data.shape)

Creating a New GlueDb
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import api
   from pyswark.core.models import collection
   from pyswark.core.io import api as io

   # Create a new empty database
   db = api.newDb()

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

Merging Databases
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import api

   db1 = api.newDb()
   db1.post('data1', 'file:./data1.csv')

   db2 = api.newDb()
   db2.post('data2', 'file:./data2.csv')

   # Merge db2 into db1
   db1.merge(db2)
   print(db1.getNames())  # ['data1', 'data2']

Using GlueHub for Multiple Databases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.gluedb import api

   hub = api.newHub()
   hub.post('market_data', market_db)
   hub.post('config', config_db)

   # Extract a specific database from the hub
   market_db = hub.extract('market_data')

