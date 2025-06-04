from typing import Union, Optional, ClassVar
import pydantic
from pydantic import field_validator, Field

from pyswark.lib.pydantic import base, ser_des
from pyswark.core.models import extractor
from pyswark.ts.datetime import Datetime
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


class Contents( extractor.Extractor ):
    pass


class Body( base.BaseModel ):
    model    : str
    contents : Union[ dict, Contents ]

    @field_validator('model')
    def _model( cls, model ):
        return model if model.startswith( 'python:' ) else f'python:{ model }'


class BodyType:

    def __init__(self, ContentsModel, BodyModel ):
        self.instances = ( dict, ContentsModel, BodyModel, pydantic.BaseModel )

    def getType(self):
        return Union[ self.instances ]

    def isInstance( self, o ):
        return isinstance( o, self.instances )


class Record( base.BaseModel ):
    Contents : ClassVar = Contents
    bodyType : ClassVar = BodyType( Contents, Body )
    info     : Union[ dict, Info ]
    body     : bodyType.getType()

    def __init__(self, body=None, name="", info=None ):
        info = self._parseInfo( name, info )
        body = self._parseBody( body )
        super().__init__( info=info, body=body )

    @classmethod
    def _parseInfo(cls, name, info):
        info = info or {}
        return { 'name': name, **info }

    @classmethod
    def _parseBody( cls, body ):
        if cls.bodyType.isInstance( body ):
            return body
        return cls.Contents.fromArgs( body )

    @field_validator( 'info' )
    def _info( cls, info ):
        if not isinstance( info, Info ):
            info = Info( **info )
        return info

    @field_validator( 'body' )
    def _body( cls, body ) -> dict:

        if isinstance( body, cls.Contents ):
            body = body.toDict()

        elif isinstance( body, Body ):
            body = body.model_dump()

        elif isinstance( body, pydantic.BaseModel ):
            body = ser_des.toDict( body )

        if not isinstance( body, dict ):
            body = cls.Contents( body ).toDict()

        if not ser_des.isSerializedDict( body ):
            body = cls.Contents( **body ).toDict()

        cls.validate( body )

        return body

    @classmethod
    def validate( cls, body ):
        """ optional validation to be added """

    def extract(self):
        model = self.acquire()

        if isinstance( model, extractor.Extractor ):
            return model.extract()
        
        return model

    def load(self, data):
        model = self.acquire()
        if not isinstance( model, self.Contents ):
            raise TypeError( f"can only load type=Contents, got type={ type(model) }" )
        model.load( data )

    def acquire(self):
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
    bodyType  = BodyType( ContentsModel, BodyModel )

    model = pydantic.create_model(
        "Record",
        __base__ = RecordModel,
        info     = ( Info, ... ),
        body     = ( bodyType.getType(), ... ),
    )

    model.Contents = ContentsModel
    return model
