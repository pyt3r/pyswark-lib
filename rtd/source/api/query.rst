query - Data Querying
=====================

The ``query`` module provides SQL-like interfaces for filtering and
selecting records from data collections. This is Layer 2 of the architecture.

Key Concepts
------------

- **Query**: A filter specification with parameters
- **Param**: A single filter condition (Equals, OneOf, etc.)
- **Collect**: Fields to return from matching records

Classes
-------

.. automodule:: pyswark.query.interface
   :members: Query, Param, Equals, OneOf
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Query
^^^^^^^^^^^

.. code-block:: python

   from pyswark.query.interface import Query, Equals, OneOf

   # Create a query with parameters
   query = Query(
       params=[
           ('status', Equals('active')),
           ('category', OneOf(['A', 'B', 'C']))
       ],
       collect=['name', 'value']
   )

   # Run against records
   results = query.runAll(records)

Query with Dict Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.query.interface import Query, Equals

   # Parameters can also be specified as a dict
   query = Query(
       params={
           'status': Equals('active'),
           'type': Equals('premium')
       }
   )

   results = query.runAll(records)

Query Methods
^^^^^^^^^^^^^

.. code-block:: python

   # runAll - records must match ALL parameters
   results = query.runAll(records)

   # runAny - records must match ANY parameter
   results = query.runAny(records)

Custom Parameters
^^^^^^^^^^^^^^^^^

You can create custom parameter types by extending ``Param``:

.. code-block:: python

   from pyswark.query.interface import Param

   class GreaterThan(Param):
       \"\"\"value > threshold\"\"\"
       inputs: float

       def __call__(self, value, records=None):
           return value > self.inputs

   # Use in query
   query = Query(params=[
       ('price', GreaterThan(100.0))
   ])

Serialization
^^^^^^^^^^^^^

Queries are fully serializable:

.. code-block:: python

   from pyswark.query.interface import Query, Equals
   from pyswark.lib.pydantic import ser_des

   query = Query(params={'status': Equals('active')})

   # Serialize
   json_str = ser_des.toJson(query)

   # Deserialize
   restored = ser_des.fromJson(json_str)

