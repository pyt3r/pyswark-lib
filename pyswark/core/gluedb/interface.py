from typing import ClassVar, Union
from pydantic import field_validator

from pyswark.lib.pydantic import base
from pyswark.core.models import contentsmodel as contentsmodel
from pyswark.core.io import api


class Db( base.BaseModel ):
    Record   : ClassVar = contentsmodel.Record
    Contents : ClassVar = contentsmodel.Contents
    records  : Union[ str, list, list[ Record ]]

    def __init__( self, records=None ):
        super().__init__( records=[] if records is None else records )

    @field_validator( 'records' )
    def _validateInstance( cls, records ) -> list:
        klass = cls.Record

        if isinstance( records, str ):
            records = api.read(records)

        if isinstance( records, list ):
            records = [ klass( **r ) if isinstance( r, dict ) else r for r in records ]

        return records

    def getData(self):
        return self.model_dump()['records']

    def getNames(self): # use sqlAlchemy?
        return [ record.name for record in self.records ]

    def load( self, name ):
        return self.acquire( name ).load()

    def acquire(self, name):
        return self._acquire( **self.getRecord( name ))

    @staticmethod
    def _acquire( name, model, contents ):
        """ the signature is specific to the Record Model annotations """
        model = model if model.startswith( 'python://' ) else f"python://{ model }"
        klass = api.read(model)
        return klass( **contents )

    def getRecord(self, name):
        return self._getRecord( name ).model_dump()

    def _getRecord(self, name):
        for record in self.records:
            if record.name == name:
                return record
        raise KeyError(f"{name=} not found")

    def getContents(self, name):
        record = self._getRecord(name)
        return record.contents

    def put( self, name, contents: Union[ contentsmodel.Contents, dict ] ):
        """ update a record in the db with new contents """
        raise NotImplementedError

    def post( self, name, contents: Union[ contentsmodel.Contents, dict] ):
        """ creates a new record in the db """
        if isinstance( contents, dict ):
            contents = self.Contents( **contents )

        record = self.Record(name=name, model=contents.getUri(), contents=contents.model_dump())
        self.records.append( record )

    def delete( self, name ):
        """ delete a record in the db """
        raise NotImplementedError

    def merge( self, otherDb ):
        """ merge the contents of another db """
        if not isinstance( otherDb, Db ):
            raise TypeError( f"can only add type DBInterface, got type={type(otherDb)}" )
        self.records += otherDb.records

    def toDb(self):
        return self
