from typing import ClassVar, Union
from pydantic import field_validator

from pyswark.lib.pydantic import base
from pyswark.gluedb import dbbackend, recordmodel
from pyswark.core.io import api


class Db( base.BaseModel ):
    Record   : ClassVar = recordmodel.Record
    Contents : ClassVar = recordmodel.Contents
    records  : Union[ str, list, list[ Record ]]

    def __init__( self, records=None ):
        super().__init__( records=[] if records is None else records )
        self._backend = dbbackend.DbBackend(self.records)

    @property
    def backend(self):
        """ backend querying engine, i.e. sqlalchemy """
        return self._backend

    @field_validator( 'records' )
    def _validateInstance( cls, records ) -> list:
        klass = cls.Record

        if isinstance( records, str ):
            records = api.read( records )

        if isinstance( records, list ):
            records = [ klass( **record ) if isinstance( record, dict ) else record for record in records ]

        return records

    def getNames(self):
        return [ record.info.name for record in self.records ]

    def get( self, name: str ):
        return self.getByName( name )

    def getByName( self, name: str ):
        query   = dbbackend.select( dbbackend.Info ).where( dbbackend.Info.name == name )
        records = self.execute( query )

        if len( records ) != 1:
            raise ValueError( f"GET query expected n=1 record, but got n={len(records)}" )

        return records.pop()

    def getByModel( self, model: str ):
        """ returns records based on the model type """
        query   = dbbackend.select( dbbackend.Body ).where( dbbackend.Body.model == model )
        records = self.execute( query )
        return records

    def getMostRecent( self ):
        with self.backend.Session() as session:
            results = session.query( dbbackend.Info ).order_by( dbbackend.Info.date_created.desc() ).all()
        return self._resultsToRecords( results )

    def execute( self, query ):
        with self.backend.Session() as session:
            results = session.execute( query ).scalars().all()
        return self._resultsToRecords( results )

    def _resultsToRecords( self, results ):
        indices = self.backend.getIndices( results )
        return [ self.records[i] for i in indices ]

    def put(self, name, body: recordmodel.Body):
        """ update a record in the db with new contents """
        record = self.getByName( name )
        record.put( body )

    def post(self, name, body: recordmodel.Body):
        """ creates a new record in the db """
        record = self.Record( body, name=name )
        self._addRecord( record )

    def delete( self, name ):
        """ delete a record in the db """
        raise NotImplementedError

    def merge( self, otherDb ):
        """ merge the contents of another db """
        if not isinstance( otherDb, Db ):
            raise TypeError( f"can only add type=Db, got type={ type(otherDb) }" )
        self._addRecords( otherDb.records )

    def _addRecords( self, records ):
        self.records += records
        self.backend.addRecords( records )

    def _addRecord( self, record ):
        self._addRecords([ record ])

    def toDb(self):
        return self

    def load(self, name):
        return self.get( name ).load()
