Getting Started
===============

Installation
------------

Install pyswark using conda:

.. code-block:: bash

   conda install -c pyt3r pyswark



Example Capabilities
--------------------

1. Serialization with Type Preservation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A core tenet of pyswark is type-preserving serialization:

.. code-block:: python

   from pydantic import BaseModel
   from pyswark.lib.pydantic import ser_des

   class Character(BaseModel):
       name: str
       role: str

   mulder = Character(name='Fox Mulder', role='FBI Agent')

   # Serialize with embedded type information
   json_data = ser_des.toJson(mulder, indent=2)
   print(json_data)
   # {
   #   "model": "__main__.Character",
   #   "contents": {"name": "Fox Mulder", "role": "FBI Agent"}
   # }

   # Deserialize - no type hint needed!
   restored = ser_des.fromJson(json_data)
   assert type(restored) == Character


2. Unified I/O
^^^^^^^^^^^^^^

Read and write data from any URI:

.. code-block:: python

   from pyswark.core.io import api as io

   # Read from package data
   df = io.read('pyswark:/data/ohlc-jpm.csv.gz')

   # Read from local file
   config = io.read('file:./config.yaml')

   # Write to file
   io.write(df, 'file:./output.csv')


3. Data Catalogs with GlueDb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create and use data catalogs:

.. code-block:: python

   from pyswark.gluedb import api

   # Connect to existing catalog
   db = api.connect('pyswark:/data/sma-example.gluedb')
   print(db.getNames())  # ['JPM', 'BAC', 'kwargs']

   # Extract data by name
   jpm_data = db.extract('JPM')

   # Create a new catalog
   new_db = api.newDb()
   new_db.post('prices', 'file:./prices.csv')
   new_db.post('config', {'window': 60})


4. Validated Arrays
^^^^^^^^^^^^^^^^^^^

Use type-safe, serializable arrays:

.. code-block:: python

   from pyswark.tensor.tensor import Vector, Matrix

   v = Vector([1.0, 2.0, 3.0, 4.0, 5.0])
   print(v.shape)  # (5,)

   m = Matrix([[1, 2, 3], [4, 5, 6]])
   print(m.shape)  # (2, 3)
