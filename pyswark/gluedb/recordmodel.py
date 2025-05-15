from typing import Union, Optional, ClassVar
import pydantic
from pydantic import field_validator, Field

from pyswark.lib.pydantic import base, ser_des
from pyswark.ts.datetime import Datetime
from pyswark.core.models.contents import Contents
from pyswark.core.io import api


class Info( base.BaseModel ):
    name          : str
    date_created  : Union[ Datetime, str, dict, None ] = Field( default='', validate_default=True )
    date_modified : Union[ Datetime, str, dict, None ] = Field( default='', validate_default=True )
    # author      : None

    @field_validator( 'date_created', 'date_modified', mode='before' )
    def _date( cls, date ):
        if not date:
            date = Datetime.now( 'UTC' )
        if isinstance( date, dict ):
            date = Datetime( **date )
        elif not isinstance( date, Datetime ):
            date = Datetime( date )
        return date


class Body( base.BaseModel ):
    model    : str
    contents : Union[ dict, Contents ]

    @field_validator('model')
    def _model( cls, model ):
        return model if model.startswith( 'python:' ) else f'python:{ model }'


class Record( base.BaseModel ):
    Contents : ClassVar = Contents
    info     : Union[ dict, Info ]
    body     : Union[ dict, Contents, Body, pydantic.BaseModel ] # order matters

    def __init__(self, body=None, name="", info=None ):
        info = info or {}
        info = { 'name': name, **info }
        super().__init__( info=info, body=body )

    @field_validator( 'info' )
    def _info( cls, info ):
        if not isinstance( info, Info ):
            info = Info( **info )
        return info

    @field_validator( 'body' )
    def _body( cls, body ) -> dict:

        if isinstance( body, cls.Contents ):
            body = { 'model': body.getUri(), 'contents': body.model_dump() }

        elif isinstance( body, Body ):
            body = body.model_dump()

        elif isinstance( body, pydantic.BaseModel ):
            body = ser_des.toDict( body )

        if not isinstance( body, dict ):
            raise TypeError(  f"expected type=dict, got {type(body)}")

        expected = { 'model', 'contents' }
        passed   = set( body.keys() )
        missing  = expected - passed
        extra    = passed - expected
        if missing or extra:
            raise ValueError( f"body has invalid keys: missing={ sorted(missing) }, extra={ sorted(extra) }" )

        cls.validate( body )

        return body

    @classmethod
    def validate( cls, body ):
        """ optional validation to be added """

    def load(self):
        model = self.get()
        if isinstance( model, self.Contents ):
            return model.load()
        return model

    def get(self):
        return self.getModel( **self.body )

    @staticmethod
    def getModel( model, contents ):
        klass = api.read( model, datahandler='python' )
        return klass( **contents )

    def put( self, body ):
        self.body = self._body( body )
        self.info.date_modified = Datetime.now()


def makeBody( ContentsModel, BodyModel=Body ):
    modelType  = Optional[ str ]
    modelValue = ContentsModel.getUri()

    return pydantic.create_model(
        "Body",
        __base__ = BodyModel,
        model    = ( modelType, modelValue ),
        contents = ( Union[ dict, ContentsModel ], ... )
    )


def makeRecord( ContentsModel, RecordModel=Record ):
    """ makes record class from a contents model """

    BodyModel = makeBody( ContentsModel )
    bodyType  = Union[ dict, ContentsModel, BodyModel, pydantic.BaseModel ]

    model = pydantic.create_model(
        "Record",
        __base__ = RecordModel,
        info     = ( Info, ... ),
        body     = ( bodyType, ... ),
    )

    model.Contents = ContentsModel
    return model
