"""
Base Model Classes
===================

This module provides enhanced Pydantic BaseModel classes with built-in
serialization capabilities. All models in pyswark should extend from
:class:`BaseModel` defined here, not directly from pydantic.

Key Features
------------
- Automatic type-preserving serialization via ``toJson()`` / ``fromJson()``
- ``extra='forbid'`` by default to catch typos in field names
- URI generation for model classes
"""

from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class ExtraForbidden( PydanticBaseModel ):
    """BaseModel variant that forbids extra fields (strict validation)."""
    model_config = ConfigDict( extra='forbid' )


class ExtraAllowed( PydanticBaseModel ):
    """BaseModel variant that allows extra fields (flexible validation)."""
    model_config = ConfigDict( extra='allow' )


class BaseModel( ExtraForbidden ):
    """
    Enhanced Pydantic BaseModel with serialization capabilities.

    This is the standard base class for all models in pyswark. It extends
    Pydantic's BaseModel with type-preserving serialization methods that
    enable "code as data" patterns.

    Example
    -------
    >>> from pyswark.lib.pydantic import base
    >>>
    >>> class MyModel(base.BaseModel):
    ...     value: str
    ...     count: int
    >>>
    >>> obj = MyModel(value="hello", count=42)
    >>> json_str = obj.toJson()  # Includes type information
    >>> restored = base.BaseModel.fromJson(json_str)
    >>> assert type(restored) == MyModel
    """

    def write( self, uri, overwrite=False, indent=2, **kw ):
        """Write the model to a URI location."""
        raise NotImplementedError

    def toJson( self, indent=2, **kw ):
        """
        Serialize this model to JSON with embedded type information.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level (default: 2).
        **kw
            Additional arguments passed to ``json.dumps()``.

        Returns
        -------
        str
            JSON string that can be deserialized with ``fromJson()``.
        """
        from pyswark.lib.pydantic import ser_des
        return ser_des.toJson( self, indent=indent, **kw )

    @staticmethod
    def fromJson( *a, **kw ):
        """
        Deserialize JSON to the original model type.

        Parameters
        ----------
        *a
            Positional arguments passed to ``ser_des.fromJson()``.
        **kw
            Keyword arguments passed to ``ser_des.fromJson()``.

        Returns
        -------
        BaseModel
            The deserialized model instance.
        """
        from pyswark.lib.pydantic import ser_des
        return ser_des.fromJson( *a, **kw )

    def toDict( self ):
        """
        Convert this model to a dictionary with embedded type information.

        Returns
        -------
        dict
            Dictionary with ``model`` and ``contents`` keys.
        """
        from pyswark.lib.pydantic import ser_des
        return ser_des.toDict( self )

    @staticmethod
    def fromDict( *a, **kw ):
        """
        Reconstruct a model from a dictionary with type information.

        Parameters
        ----------
        *a
            Positional arguments passed to ``ser_des.fromDict()``.
        **kw
            Keyword arguments passed to ``ser_des.fromDict()``.

        Returns
        -------
        BaseModel
            The reconstructed model instance.
        """
        from pyswark.lib.pydantic import ser_des
        return ser_des.fromDict( *a, **kw )

    @classmethod
    def getUri(cls):
        """
        Get the fully-qualified Python path for this model class.

        Returns
        -------
        str
            The module and class name (e.g., ``"mypackage.models.MyModel"``).
        """
        return f"{ cls.__module__}.{ cls.__qualname__}"
