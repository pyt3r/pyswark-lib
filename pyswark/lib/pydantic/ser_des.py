import pydoc
import json
from typing import TypeVar, Type

from pydantic import field_validator, BaseModel
from pyswark.lib.pydantic import base

BaseModelInst = TypeVar( 'pydantic.BaseModel' )
BaseModelType = Type[ BaseModel ]


def toJson( model: BaseModelType, **kw ) -> str:
    data = toDict( model )
    return json.dumps( data, **kw )

def fromJson( loadable: str ) -> BaseModelType:
    data = json.loads( loadable )
    return fromDict( data )

def toDict( model: BaseModelType ) -> dict:
    dictModel = ToDictModel( model=model, contents=model )
    return dictModel.model_dump()

def fromDict( data: dict ) -> BaseModelType:
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