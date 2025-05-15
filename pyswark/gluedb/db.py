from typing import Optional, Union
from pydantic import Field, create_model

from pyswark.core.io import contents
from pyswark.gluedb import dbmodel, recordmodel


class Contents( contents.Contents ):
    uri         : str
    datahandler : Optional[ str ] = ""
    kw          : Optional[ dict ] = Field( default_factory=lambda: {} )

    def load( self ):
        return super().read()


def _makeDb( ContentsModel, RecordModel, base ):
    """ makes a db class from a contents model """
    RecordModel = recordmodel.makeRecord( ContentsModel, RecordModel )

    Model = create_model(
        "GlueDb",
        __base__ = base,
        records  = ( Union[ str, list, list[ RecordModel ]], ... )
    )
    # ClassVars
    Model.Record   = RecordModel
    Model.Contents = ContentsModel

    return Model


_Record = recordmodel.makeRecord( Contents )
Record  = recordmodel.makeRecord( Contents, _Record )

_GlueDb = _makeDb( Contents, Record, dbmodel.Db )


class GlueDb( _GlueDb ):

    def merge( self, otherDb ):
        """ merge the contents of another db """
        if not isinstance( otherDb, GlueDb ):
            raise TypeError( f"can only add type=GlueDb, got type={ type(otherDb) }" )
        super().merge( otherDb )


def makeDb( ContentsModel, RecordModel=Record ):
    return _makeDb( ContentsModel, RecordModel, GlueDb  )
