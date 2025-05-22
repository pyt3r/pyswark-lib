from typing import ClassVar, Union
from pydantic import field_validator

from pyswark.lib.pydantic import base

from pyswark.core.io import api

from pyswark.gluedb import dbbackend, recordmodel
from pyswark.gluedb import sql, table


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
        query   = sql.select( table.Info )
        results = self.getByQuery( query, returnBackend=True )
        return [ r.name for r in results ]

    def get( self, name: str ):
        return self.getByName( name )

    def getByName( self, name: str ):
        query   = self._getByNameQuery( name )
        records = self.getByQuery( query )
        self._assertOneResult( records )
        return records.pop()

    @staticmethod
    def _getByNameQuery( name ):
        return sql.select( table.Info ).where( table.Info.name == name )

    @staticmethod
    def _assertOneResult( records ):
        if len( records ) != 1:
            raise ValueError( f"Expected query to return n=1 record, but got n={len(records)}" )

    def getByModel( self, model: str ):
        """ returns records based on the model type """
        query   = sql.select( table.Body ).where( table.Body.model == model )
        records = self.getByQuery( query )
        return records

    def getMostRecent( self ):
        with self.backend.Session() as session:
            results = session.query( table.Info ).order_by( table.Info.date_created.desc() ).all()
        return self._resultsToRecords( results )

    def getByQuery( self, query, returnBackend=False ):
        with self.backend.Session() as session:
            results = session.execute( query ).scalars().all()
        if returnBackend:
            return results
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
        if isinstance( body, self.Record ):
            body = body.body
        record = self.Record( body, name=name )
        self._addRecord( record )

    def delete( self, name ):
        """ delete a record in the db """
        self.deleteByName( name )

    def deleteByName( self, name ):
        """ delete a record in the db """
        query   = self._getByNameQuery( name )
        records = self.getByQuery( query )
        self._assertOneResult( records )

        results = self.backend.delete( query )
        self._delete( results )

    def _delete( self, results ):
        for result in results:
            self.records.pop( result.index )

    def merge( self, otherDb ):
        """ merge the contents of another db """
        if not isinstance( otherDb, Db ):
            raise TypeError( f"can only add type=Db, got type={ type(otherDb) }" )
        self._addRecords( otherDb.records )

    def _addRecords( self, records ):
        # TO DO - validate one name
        self.records += records
        self.backend.addRecords( records )

    def _addRecord( self, record ):
        self._addRecords([ record ])

    def toDb(self):
        return self

    def load(self, name):
        return self.get( name ).load()
