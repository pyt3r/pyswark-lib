"""
Time Series Vector
==================

This module provides the TsVector class, a time series data structure
combining a datetime index with numeric values.
"""

from pydantic import model_validator, field_validator
from pyswark.lib.pydantic import base

from pyswark.tensor import tensor
from pyswark.core.models.datetime import DatetimeList


class TsVector( base.BaseModel ):
    """
    A time series with datetime index and numeric values.

    Combines a DatetimeList index with a Vector of values, ensuring
    they have matching lengths.

    Parameters
    ----------
    index : DatetimeList or array-like
        The datetime index.
    values : Vector or array-like
        The numeric values.

    Example
    -------
    >>> from pyswark.ts.tsvector import TsVector
    >>> ts = TsVector(
    ...     index=['2024-01-01', '2024-01-02', '2024-01-03'],
    ...     values=[100.0, 101.5, 99.8]
    ... )
    >>> print(len(ts))  # 3
    """
    index  : DatetimeList
    values : tensor.Vector

    @property
    def dt(self):
        return self.index.dt

    @field_validator( "index", mode='before' )
    def _index(cls, index ):
        return index if isinstance( index, DatetimeList ) else DatetimeList( index )

    @field_validator( "values", mode='before' )
    def _values(cls, values ):
        return values if isinstance( values, tensor.Vector ) else tensor.Vector( values )

    @model_validator( mode='after' )
    def _after(self):
        if len( self.dt ) != len( self.values ):
            raise ValueError( f"lengths must match: { len( self.dt )= }, { len( self.values )= }" )
        return self
