"""
Tensor Module
=============

This module provides Pydantic-validated wrappers around numpy arrays.
Tensors are serializable, type-safe, and integrate with the pyswark
serialization system.

Classes
-------
Vector
    A 1-dimensional validated array.
Matrix
    A 2-dimensional validated array.
Tensor
    Base class for n-dimensional arrays.

Example
-------
>>> from pyswark.tensor.tensor import Vector, Matrix
>>>
>>> v = Vector([1.0, 2.0, 3.0, 4.0, 5.0])
>>> print(v.shape)  # (5,)
>>>
>>> m = Matrix([[1, 2, 3], [4, 5, 6]])
>>> print(m.shape)  # (2, 3)
>>>
>>> # Tensors are serializable
>>> print(v.model_dump())
"""

import numpy as np
from typing import Any, Union, List, TypeVar
from pydantic import model_validator, field_validator, Field

from pyswark.core.models import xputs, converter

NumpyArray = TypeVar( 'numpy.array' )

class Inputs( xputs.BaseInputs ):
    """
    Input specification for Tensor creation.

    Parameters
    ----------
    data : array-like
        The array data (list, tuple, or numpy array).
    dtype : str, optional
        The numpy dtype (e.g., 'float64', 'int32').
    """
    data  : Union[ NumpyArray, List ]
    dtype : Any = Field( None )

    @field_validator( 'dtype', mode='before' )
    def _dtype(cls, dtype):
        return str( np.dtype( dtype ))

    @model_validator( mode='after' )
    def after(self):
        data  = self.data
        dtype = self.dtype

        if isinstance( data, np.ndarray ) and dtype is None:
            dtype = self._dtype( data.dtype )
            data  = data.tolist()

        if isinstance( data, tuple ):
            data = list( data )

        if not isinstance( data, list ):
            raise TypeError( f"{ type(data)= } is not array-like" )

        if not dtype:
            dtype = self._dtype( np.asarray( data ).dtype )

        self.data  = data
        self.dtype = dtype

        return self


class Tensor( converter.ConverterModel ):
    """
    Base class for validated numpy arrays.

    Wraps numpy arrays with Pydantic validation, enabling serialization
    and type-safe array operations.

    Parameters
    ----------
    inputs : Inputs or array-like
        The input data specification.

    Attributes
    ----------
    tensor : numpy.ndarray
        The underlying numpy array.
    shape : tuple
        The array shape.
    """
    inputs: Inputs

    def __len__(self):
        return len( self.tensor )

    @property
    def shape(self):
        """Return the shape of the tensor."""
        return self.tensor.shape

    @property
    def tensor(self):
        """Return the underlying numpy array."""
        return self.outputs

    @classmethod
    def convert( cls, inputs: Inputs ) -> np.ndarray:
        data   = inputs.data
        dtype  = inputs.dtype
        tensor = np.asarray( data )
        tensor = tensor.astype( dtype ) if dtype else tensor
        return cls._validateTensor( tensor )

    @staticmethod
    def _validateTensor( tensor: np.ndarray ) -> np.ndarray:
        return tensor


class Vector( Tensor ):
    """
    A validated 1-dimensional array.

    Validates that the input data is exactly 1-dimensional.

    Example
    -------
    >>> v = Vector([1.0, 2.0, 3.0])
    >>> print(v.shape)  # (3,)
    >>> print(v.vector)  # array([1., 2., 3.])
    """
    inputs: Inputs

    @property
    def vector(self):
        """Return the underlying 1D numpy array."""
        return self.tensor

    @staticmethod
    def _validateTensor( tensor: np.ndarray ) -> np.ndarray:
        shape = tensor.shape
        if len(shape) != 1:
            raise ValueError(f"Array tensor must be 1 dimensional: got {shape=}" )

        return tensor


class Matrix( Tensor ):
    """
    A validated 2-dimensional array.

    Validates that the input data is exactly 2-dimensional.

    Example
    -------
    >>> m = Matrix([[1, 2, 3], [4, 5, 6]])
    >>> print(m.shape)  # (2, 3)
    >>> print(m.matrix)
    """
    inputs: Inputs

    @property
    def matrix(self):
        """Return the underlying 2D numpy array."""
        return self.tensor

    @staticmethod
    def _validateTensor( tensor: np.ndarray ) -> np.ndarray:
        shape = tensor.shape
        if len(shape) != 2 :
            raise ValueError(f"Matrix tensor must be 2 dimensional: got {shape=}" )

        return tensor
