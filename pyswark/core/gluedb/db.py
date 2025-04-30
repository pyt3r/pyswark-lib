from typing import Optional, Union, List
from pydantic import Field, create_model

from pyswark.core.models import contentsmodel
from pyswark.core.io import api
from pyswark.core.gluedb import interface


class Contents(contentsmodel.Contents):
    uri         : str
    datahandler : Optional[ str ] = ""
    kw          : Optional[ dict ] = Field( default_factory=lambda: {} )

    def load( self ):
        return api.read( self.uri, self.datahandler, **self.kw )


def _makeDb( ContentsModel, RecordModel, base ):
    """ makes a db class from a contents model """
    RecordModel = contentsmodel.makeRecord(ContentsModel, RecordModel)

    Model = create_model(
        "GlueDb",
        __base__ = base,
        records  = ( Union[ str, List, List[ RecordModel ]], ... )
    )
    # ClassVars
    Model.Record   = RecordModel
    Model.Contents = ContentsModel

    return Model


_Record = contentsmodel.makeRecord(Contents)
Record  = contentsmodel.makeRecord(Contents, _Record)

_GlueDb = _makeDb( Contents, Record, interface.Db )
GlueDb  = _makeDb( Contents, Record, _GlueDb )

def makeDb( ContentsModel ):
    return _makeDb( ContentsModel, Record, GlueDb  )
