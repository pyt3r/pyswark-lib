tensor - Validated Arrays
=========================

The ``tensor`` module provides Pydantic-validated wrappers around numpy arrays.
This is Layer 2 of the architecture.

Key Features
------------

- **Serializable arrays**: Numpy arrays that can be serialized/deserialized
- **Shape validation**: Enforce dimensionality constraints
- **Type safety**: Validate dtype and shape at creation time

Classes
-------

.. automodule:: pyswark.tensor.tensor
   :members: Tensor, Vector, Matrix, Inputs
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Creating Vectors
^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.tensor.tensor import Vector
   import numpy as np

   # Create from list
   v = Vector([1.0, 2.0, 3.0, 4.0, 5.0])
   print(v.shape)   # (5,)
   print(v.vector)  # array([1., 2., 3., 4., 5.])

   # Create from numpy array
   arr = np.array([10, 20, 30])
   v2 = Vector(arr)

   # Specify dtype
   v3 = Vector([1, 2, 3], dtype='float32')

Creating Matrices
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.tensor.tensor import Matrix

   # Create from nested lists
   m = Matrix([[1, 2, 3], [4, 5, 6]])
   print(m.shape)   # (2, 3)
   print(m.matrix)

   # Create from numpy array
   arr = np.zeros((3, 4))
   m2 = Matrix(arr)

Serialization
^^^^^^^^^^^^^

Tensors are fully serializable:

.. code-block:: python

   from pyswark.tensor.tensor import Vector
   from pyswark.lib.pydantic import ser_des

   v = Vector([1.0, 2.0, 3.0])

   # Serialize to dict
   data = v.model_dump()
   # {'inputs': {'data': [1.0, 2.0, 3.0], 'dtype': 'float64'}}

   # Full serialization with type info
   json_str = ser_des.toJson(v)

   # Deserialize
   restored = ser_des.fromJson(json_str)
   assert type(restored) == Vector

Shape Validation
^^^^^^^^^^^^^^^^

Vectors must be 1-dimensional, Matrices must be 2-dimensional:

.. code-block:: python

   from pyswark.tensor.tensor import Vector, Matrix

   # This works
   v = Vector([1, 2, 3])

   # This raises ValueError
   try:
       v = Vector([[1, 2], [3, 4]])  # 2D data
   except ValueError as e:
       print(e)  # "Array tensor must be 1 dimensional..."

   # Similarly for Matrix
   m = Matrix([[1, 2], [3, 4]])  # OK
   # Matrix([1, 2, 3])  # ValueError - must be 2D

