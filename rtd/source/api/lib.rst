lib
==============================

The ``lib`` module provides foundational serialization and utility classes.
This is Layer 0 of the pyswark architecture - all other modules build on top of it.

Key Features
------------

- **Type-preserving serialization**: Serialize Pydantic models with embedded type information
- **Enhanced BaseModel**: Standard base class for all pyswark models
- **Filesystem abstraction**: Unified file system access via fsspec
- **Enum utilities**: Extended enum functionality with alias support

Serialization (ser_des)
-----------------------

The ``ser_des`` module provides functions for serializing Pydantic models with
embedded type information, enabling automatic deserialization without specifying
the target type.

.. automodule:: pyswark.lib.pydantic.ser_des
   :members: toJson, fromJson, toDict, fromDict
   :undoc-members:
   :show-inheritance:

Base Models
-----------

The ``base`` module provides enhanced Pydantic base classes.

.. automodule:: pyswark.lib.pydantic.base
   :members: BaseModel, ExtraForbidden, ExtraAllowed
   :undoc-members:
   :show-inheritance:

Enum Utilities
--------------

The ``enum`` module provides enhanced enum classes with utility methods.

.. automodule:: pyswark.lib.enum
   :members: Enum, Mixin
   :undoc-members:
   :show-inheritance:

AliasEnum
---------

The ``aenum`` module provides enum classes with alias support, allowing
multiple names to reference the same member.

.. automodule:: pyswark.lib.aenum
   :members: AliasEnum, Alias, AliasEnumError
   :undoc-members:
   :show-inheritance:

Filesystem (fsspec)
-------------------

The ``fsspec`` submodule provides unified filesystem access with custom
protocol support.

.. automodule:: pyswark.lib.fsspec.fsspec
   :members: open, filesystem
   :undoc-members:
   :show-inheritance:

.. automodule:: pyswark.lib.fsspec.implementations
   :members: PythonFileSystem, PythonFile
   :undoc-members:
   :show-inheritance:


Usage Examples
--------------

Type-Preserving Serialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pydantic import BaseModel
   from pyswark.lib.pydantic import ser_des

   class Character(BaseModel):
       name: str
       role: str

   # Create an instance
   mulder = Character(name='Fox Mulder', role='FBI Agent')

   # Serialize with type information
   json_data = ser_des.toJson(mulder, indent=2)
   # Output:
   # {
   #   "model": "__main__.Character",
   #   "contents": {
   #     "name": "Fox Mulder",
   #     "role": "FBI Agent"
   #   }
   # }

   # Deserialize - no type hint needed!
   restored = ser_des.fromJson(json_data)
   assert type(restored) == Character

Creating Custom Models
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.lib.pydantic import base

   class MyModel(base.BaseModel):
       value: str
       count: int

   obj = MyModel(value="hello", count=42)
   
   # Built-in serialization methods
   json_str = obj.toJson()
   restored = base.BaseModel.fromJson(json_str)

Using Enum Utilities
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.lib.enum import Enum

   class Status(Enum):
       ACTIVE = 1
       INACTIVE = 0
       PENDING = 2

   # Get dict of all members
   Status.asDict()
   # {'ACTIVE': 1, 'INACTIVE': 0, 'PENDING': 2}

   # Generate Python code
   print(Status.asPythonCode('MyStatus'))

   # Create enum dynamically
   DynamicStatus = Enum.createDynamically(
       {'ON': True, 'OFF': False},
       'DynamicStatus'
   )

Using AliasEnum
^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.lib.aenum import AliasEnum, Alias

   class Protocol(AliasEnum):
       HTTP = 80, Alias('http', 'web')
       HTTPS = 443, Alias('https', 'secure')
       SSH = 22

   # Access by name
   Protocol.HTTP.value  # 80

   # Access by alias
   Protocol.get('http').value   # 80
   Protocol.get('web').value    # 80
   Protocol.get('secure').value # 443

   # View aliases
   Protocol.HTTP.aliases  # {'HTTP', 'http', 'web'}

   # Create mapping from all aliases to values
   Protocol.toMapping()
   # {'HTTP': 80, 'http': 80, 'web': 80, 'HTTPS': 443, ...}

   # Safe lookup with default
   Protocol.tryGet('unknown', default=None)  # None

Using Filesystem Abstraction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.lib.fsspec import fsspec

   # Get a filesystem for a protocol
   fs = fsspec.filesystem('python')

   # Check if a Python object exists
   fs.exists('os.path.join')  # True

   # Open and locate a Python object
   with fs.open('json.loads') as f:
       loads_func = f.locate()
