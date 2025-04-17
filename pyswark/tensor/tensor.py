import numpy as np
from typing import Any, Union, List, TypeVar
from pydantic import model_validator, field_validator, Field

from pyswark.core.models import xputs, converter

NumpyArray = TypeVar( 'numpy.array' )

class Inputs( xputs.BaseInputs ):
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
    inputs: Inputs

    def __len__(self):
        return len( self.tensor )

    @property
    def shape(self):
        return self.tensor.shape

    @property
    def tensor(self):
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

    @property
    def vector(self):
        return self.tensor

    @staticmethod
    def _validateTensor( tensor: np.ndarray ) -> np.ndarray:
        shape = tensor.shape
        if len(shape) != 1:
            raise ValueError(f"Array tensor must be 1 dimensional: got {shape=}" )

        return tensor


class Matrix( Tensor ):

    @property
    def matrix(self):
        return self.tensor

    @staticmethod
    def _validateTensor( tensor: np.ndarray ) -> np.ndarray:
        shape = tensor.shape
        if len(shape) != 2 :
            raise ValueError(f"Matrix tensor must be 2 dimensional: got {shape=}" )

        return tensor
