"""
Serialization and Deserialization Utilities
============================================

This module provides type-preserving serialization for Pydantic models.
The key feature is that serialized JSON embeds the model's fully-qualified
class name, enabling automatic deserialization without specifying the type.

Example
-------
>>> from pyswark.lib.pydantic import ser_des
>>> from pydantic import BaseModel
>>>
>>> class Character(BaseModel):
...     name: str
...     role: str
>>>
>>> mulder = Character(name='Fox Mulder', role='FBI Agent')
>>> json_data = ser_des.toJson(mulder)
>>> restored = ser_des.fromJson(json_data)  # No type hint needed!
>>> assert type(restored) == Character
"""

import pydoc
import json
from typing import TypeVar, Type

from pydantic import field_validator, BaseModel
from pyswark.lib.pydantic import base

BaseModelInst = TypeVar( 'pydantic.BaseModel' )
BaseModelType = Type[ BaseModel ]


def toJson( model: BaseModelType, **kw ) -> str:
    """
    Serialize a Pydantic model to JSON with embedded type information.

    The serialized output includes the model's fully-qualified class name,
    enabling automatic deserialization via :func:`fromJson`.

    Parameters
    ----------
    model : BaseModel
        A Pydantic model instance to serialize.
    **kw
        Additional keyword arguments passed to ``json.dumps()``
        (e.g., ``indent=2`` for pretty-printing).

    Returns
    -------
    str
        JSON string with structure: ``{"model": "module.Class", "contents": {...}}``

    See Also
    --------
    fromJson : Deserialize JSON back to the original model type.
    toDict : Convert to dict without JSON encoding.

    Example
    -------
    >>> json_str = toJson(my_model, indent=2)
    """
    data = toDict( model )
    return json.dumps( data, **kw )

def fromJson( loadable: str ) -> BaseModelType:
    """
    Deserialize JSON to its original Pydantic model type.

    The JSON must have been created with :func:`toJson` (or have the same
    structure with ``model`` and ``contents`` keys).

    Parameters
    ----------
    loadable : str
        JSON string containing embedded type information.

    Returns
    -------
    BaseModel
        An instance of the original model class.

    Raises
    ------
    TypeError
        If the ``model`` path cannot be resolved or is not a BaseModel subclass.

    See Also
    --------
    toJson : Serialize a model with type information.
    fromDict : Deserialize from a dictionary.

    Example
    -------
    >>> restored = fromJson(json_string)
    >>> print(type(restored).__name__)
    'Character'
    """
    data = json.loads( loadable )
    return fromDict( data )

def toDict( model: BaseModelType ) -> dict:
    """
    Convert a Pydantic model to a dictionary with embedded type information.

    Parameters
    ----------
    model : BaseModel
        A Pydantic model instance.

    Returns
    -------
    dict
        Dictionary with ``model`` (class path) and ``contents`` (model data) keys.

    See Also
    --------
    fromDict : Reconstruct the model from the dictionary.
    """
    dictModel = ToDictModel( model=model, contents=model )
    return dictModel.model_dump()

def fromDict( data: dict ) -> BaseModelType:
    """
    Reconstruct a Pydantic model from a dictionary with type information.

    Parameters
    ----------
    data : dict
        Dictionary with ``model`` and ``contents`` keys.

    Returns
    -------
    BaseModel
        An instance of the original model class.

    See Also
    --------
    toDict : Create a typed dictionary from a model.
    """
    dictModel = FromDictModel( **data )
    return dictModel.load()


def isSerializedDict( data: dict ):
    """ simple check to see if the data has the correct keys """
    if isinstance( data, dict ):
        expected = set( FromDictModel.model_fields.keys() )
        passed   = set( data.keys() )
        missing  = expected - passed
        extra    = passed - expected
        return not ( missing or extra )


class ToDictModel( base.BaseModel ):
    model    : BaseModelInst
    contents : BaseModelInst

    @field_validator( 'model' )
    @classmethod
    def mustBeBaseModelInstance( cls, model: BaseModelInst ) -> str:
        cls._mustBeBaseModelInstance( model )
        klass = model.__class__
        return f"{ klass.__module__ }.{ klass.__name__ }"

    @field_validator( 'contents' )
    @classmethod
    def mustBeDumpable( cls, model: BaseModelInst ) -> dict:
        cls._mustBeBaseModelInstance( model )
        return model.model_dump()

    @staticmethod
    def _mustBeBaseModelInstance( model: BaseModelInst ) -> None:
        if not isinstance( model, BaseModel ):
            raise TypeError( f'{ model= } must be an instance of { BaseModel }')


class FromDictModel( base.BaseModel ):
    model    : str
    contents : dict

    @field_validator( 'model' )
    @classmethod
    def mustBeBaseModelSubclass( cls, model: str ) -> BaseModelType:
        Model = pydoc.locate( model )
        valid = Model and issubclass( Model, BaseModel )
        if not valid:
            raise TypeError( f'{ model=} must a subclass of { BaseModel }')
        return Model

    def load(self):
        return self.model( **self.contents )