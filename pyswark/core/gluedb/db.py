from typing import Optional, Union, List
from pydantic import Field, create_model

from pyswark.core.models import contents
from pyswark.core.io import api
from pyswark.core.gluedb import interface


class Contents( interface.Contents ):
    uri         : str
    datahandler : Optional[ str ] = ""
    kw          : Optional[ dict ] = Field( default_factory=lambda: {} )

    def load( self ):
        return api.read( self.uri, self.datahandler, **self.kw )


def _makeDb( ContentsModel: contents.Contents, RecordModel: contents.Record, base: interface.Db ):
    """ makes a db class from a contents model """
    RecordModel = contents.makeRecord( ContentsModel, RecordModel )

    Model = create_model(
        "GlueDb",
        __base__ = base,
        records  = ( Union[ str, List, List[ RecordModel ]], ... )
    )
    # ClassVars
    Model.Record   = RecordModel
    Model.Contents = ContentsModel

    return Model


Record  = contents.makeRecord( Contents, interface.Record )
_GlueDb = _makeDb( Contents, Record, interface.Db )
GlueDb  = _makeDb( Contents, Record, _GlueDb )

def makeDb( ContentsModel: interface.Contents ):
    return _makeDb( ContentsModel, Record, GlueDb  )
