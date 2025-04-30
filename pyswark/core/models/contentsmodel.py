from typing import Union, Optional
from pydantic import create_model, field_validator
from pyswark.lib.pydantic.base import BaseModel
from pyswark.core.io import api


class Loader( BaseModel ):

    def load( self ):
        return self


class Contents( Loader ):

    def __init__( self, *a, **kw ):
        base = f"python://{ Contents.__module__}.{ Contents.__name__}"
        if self.getUri() == base:
            raise TypeError( f"Cannot use abstract base implementation='{ base }'")

        super().__init__( *a, **kw )

    @classmethod
    def getUri(cls):
        return f"python://{ cls.__module__}.{ cls.__name__}"


class Record( BaseModel ):
    name     : str
    model    : str
    contents : Union[ Contents, dict ]

    @field_validator('model')
    def _model( cls, model ):
        return model if model.startswith( 'python:' ) else f'python:{ model }'

    def load(self):
        klass = api.read( self.model )
        return klass( **self.contents.model_dump() )


def makeRecord( ContentsModel, RecordModel=Record ):
    """ makes record class from a contents model """

    modelType  = Optional[ str ]
    modelValue = ContentsModel.getUri()

    return create_model(
        "Record",
        __base__ = RecordModel,
        name     = ( str, ... ),
        model    = ( modelType, modelValue ),
        contents  = ( ContentsModel, ...)
    )

Record = makeRecord( Contents )
