from typing import ClassVar, Union
from pydantic import field_validator

from pyswark.lib.pydantic import base
from pyswark.core.gluedb import recordmodel
from pyswark.core.io import api


class Db( base.BaseModel ):
    Record   : ClassVar = recordmodel.Record
    Contents : ClassVar = recordmodel.Contents
    records  : Union[ str, list, list[ Record ]]

    def __init__( self, records=None ):
        super().__init__( records=[] if records is None else records )

    @field_validator( 'records' )
    def _validateInstance( cls, records ) -> list:
        klass = cls.Record

        if isinstance( records, str ):
            records = api.read(records)

        if isinstance( records, list ):
            records = [ klass( **record ) if isinstance( record, dict ) else record for record in records ]

        return records

    def getNames(self):
        return [ record.info.name for record in self.records ]

    def get(self, name): # use sqlAlchemy for faster retrieval?
        for record in self.records:
            if record.info.name == name:
                return record
        raise KeyError( f"{name=} not found" )

    def put(self, name, body: recordmodel.BodyType):
        """ update a record in the db with new contents """
        raise NotImplementedError

    def post(self, name, body: recordmodel.BodyType):
        """ creates a new record in the db """
        self.records.append(recordmodel.Record(body, name=name))

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

    def load(self, name):
        return self.get( name ).load()