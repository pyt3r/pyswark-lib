from typing import Optional, Union, List
from pydantic import Field, create_model

from pyswark.core.io import api
from pyswark.core.gluedb import interface


class Contents( interface.Contents ):
    uri         : str
    datahandler : Optional[ str ] = ""
    kw          : Optional[ dict ] = Field( default_factory=lambda: {} )

    def load( self ):
        return api.read( self.uri, self.datahandler, **self.kw )


def _makeDb( ContentsModel: interface.Contents, RecordModel: interface.Record, base: interface.Db ):
    """ makes a db class from a contents model """
    RecordModel = _makeRecord( ContentsModel, RecordModel )

    Model = create_model(
        "GlueDb",
        __base__ = base,
        records  = ( Union[ str, List, List[ RecordModel ]], ... )
    )
    # ClassVars
    Model.Record   = RecordModel
    Model.Contents = ContentsModel

    return Model


def _makeRecord( ContentsModel: interface.Contents, base: interface.Record ):
    """ makes record class from a contents model """

    modelType  = Optional[ str ]
    modelValue = ContentsModel.getUri()

    return create_model(
        "Record",
        __base__ = base,
        name     = ( str, ... ),
        model    = ( modelType, modelValue ),
        contents  = ( ContentsModel, ...)
    )


Record  = _makeRecord( Contents, interface.Record )
_GlueDb = _makeDb( Contents, Record, interface.Db )
GlueDb  = _makeDb( Contents, Record, _GlueDb )

def makeDb( ContentsModel: interface.Contents ):
    return _makeDb( ContentsModel, Record, GlueDb  )
