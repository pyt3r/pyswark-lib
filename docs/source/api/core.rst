core - I/O and Models
=====================

The ``core`` module provides fundamental I/O operations and model abstractions.
This is Layer 1, built on top of the ``lib`` layer.

Key Features
------------

- **Unified I/O API**: Read/write any data source with a consistent URI interface
- **URI handling**: Support for file:, pyswark:, python:, http: schemes
- **Model abstractions**: Converters, extractors, and data models

I/O API
-------

The ``io`` submodule provides the primary interface for reading and writing data.

.. automodule:: pyswark.core.io.api
   :members: read, write, acquire, isUri
   :undoc-members:
   :show-inheritance:

URI Schemes
-----------

pyswark supports multiple URI schemes:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Scheme
     - Example
     - Description
   * - ``file:``
     - ``file:./data.csv``
     - Local filesystem
   * - ``pyswark:``
     - ``pyswark:/data/ohlc-jpm.csv.gz``
     - Package data files
   * - ``python:``
     - ``python://module.Class``
     - Python objects by import path
   * - ``http:``/``https:``
     - ``https://example.com/data.json``
     - Remote URLs

Usage Examples
--------------

Reading Data
^^^^^^^^^^^^

.. code-block:: python

   from pyswark.core.io import api as io

   # Read from package data
   df = io.read('pyswark:/data/ohlc-jpm.csv.gz')

   # Read from local file
   config = io.read('file:./config.yaml')

   # Read from URL
   data = io.read('https://example.com/api/data.json')

   # Read with custom options (passed to pandas)
   df = io.read('file:./data.csv', index_col=0)

Writing Data
^^^^^^^^^^^^

.. code-block:: python

   from pyswark.core.io import api as io

   # Write DataFrame to CSV
   io.write(df, 'file:./output.csv', index=False)

   # Write config to YAML
   io.write(config, 'file:./config.yaml')

   # Write model to JSON with type info
   io.write(model, 'file:./model.json')

Validating URIs
^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.core.io import api as io

   io.isUri('file:./data.csv')      # True
   io.isUri('pyswark:/data/foo')    # True
   io.isUri('/plain/path.csv')      # False

Core Models
-----------

The ``models`` submodule provides base classes for data handling, database operations,
and model patterns.

Input/Output Base Classes
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyswark.core.models.xputs
   :members: BaseInputs, BaseOutputs
   :undoc-members:
   :show-inheritance:

Collection Models
^^^^^^^^^^^^^^^^^

Serializable collections that preserve type information:

.. automodule:: pyswark.core.models.collection
   :members: List, Dict, Tuple, Set
   :undoc-members:
   :show-inheritance:

Model Patterns
^^^^^^^^^^^^^^

Base classes for different model patterns:

.. automodule:: pyswark.core.models.converter
   :members: ConverterModel
   :undoc-members:
   :show-inheritance:

.. automodule:: pyswark.core.models.function
   :members: FunctionModel
   :undoc-members:
   :show-inheritance:

Database Models
^^^^^^^^^^^^^^^

Base classes for database operations:

.. automodule:: pyswark.core.models.db
   :members: Db, MixinDb
   :undoc-members:
   :show-inheritance:

.. automodule:: pyswark.core.models.record
   :members: Record
   :undoc-members:
   :show-inheritance:

.. automodule:: pyswark.core.models.info
   :members: Info
   :undoc-members:
   :show-inheritance:

.. automodule:: pyswark.core.models.body
   :members: Body
   :undoc-members:
   :show-inheritance:

Primitive Models
^^^^^^^^^^^^^^^^

Type-safe wrappers for primitive values:

.. automodule:: pyswark.core.models.primitive
   :members: Int, Float, String, Bool
   :undoc-members:
   :show-inheritance:

