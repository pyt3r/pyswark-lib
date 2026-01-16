from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.orm import selectinload
from typing import ClassVar, Union
from functools import singledispatchmethod

from pydantic import Field
from pyswark.lib.pydantic import base
from pyswark.lib import enum

from pyswark.core.models import mixin, record, body, info


class Db( base.BaseModel, mixin.TypeCheck ):
    """Base class for a database."""
    AllowedTypes     : ClassVar[ list[ Union[ str, type ] ] ] = []
    AllowedInstances : ClassVar[ list[ Union[ str, type ] ] ] = []

    records : list[ record.Record ] = Field( default_factory=list )

    @property
    def enum(self):
        return enum.Enum.createDynamically({ n: n for n in self.getNames() })

    def postAll( self, objs ):
        sqlModel = self.asSQLModel()
        sqlModel.postAll( objs )
        self.records = sqlModel.asModel().records
        return self

    def post( self, obj, name=None ):
        dbModel = self.asSQLModel()
        rec = dbModel.post( obj, name=name )
        model = rec.asModel()
        self.records.append( model )
        return model

    @singledispatchmethod
    @classmethod
    def _post( cls, obj, name=None ):
        """Post an object to the database. Dispatches based on type."""
        raise NotImplementedError( f"post() not implemented for type { type(obj) }" )

    @_post.register( record.Record )
    @classmethod
    def _post_record( cls, rec: record.Record, name=None ):
        """Post a Record directly."""
        if name:
            rec.info.name = name
        return cls._post_after( rec )

    @_post.register( body.Body )
    @classmethod
    def _post_body( cls, bod: body.Body, name=None ):
        """Post a Body directly."""
        if name is None:
            raise ValueError( f"name is required for type={ type(bod) }" )
        rec = record.Record( info={ 'name': name }, body=bod )
        return cls._post_after( rec )

    @_post.register( base.BaseModel )
    @classmethod
    def _post_model( cls, model: base.BaseModel, name=None ):
        """Post a BaseModel (wraps in a Record)."""
        if not name:
            raise ValueError( f"name is required for type={ type(model) }" )
        rec = record.Record( info={ 'name': name }, body={ 'model': model } )
        return cls._post_after( rec )

    @classmethod
    def _post_after( cls, rec: record.Record ):
        """Validate the record and return it."""
        cls.checkIfInstance( rec, record.Record )
        cls._checkModel( rec.body.model )
        return rec

    @classmethod
    def _checkModel( cls, model ):
        cls.checkIfAllowedType( model, cls.AllowedTypes )
        cls.checkIfAllowedSubType( model, cls.AllowedInstances )

    def getByName( self, name ): 
        sqlModel = self.asSQLModel()
        result   = sqlModel.getByName( name )
        return result if result is None else result.asModel()

    def deleteByName( self, name ):
        sqlModel     = self.asSQLModel()
        success      = sqlModel.deleteByName( name )
        self.records = sqlModel.asModel().records
        return success

    def put( self, obj, name=None ):
        dbModel = self.asSQLModel()
        sqlModel = dbModel.put( obj, name=name )
        self.records = dbModel.asModel().records
        return sqlModel.asModel()

    def asSQLModel( self, *a, **kw ):
        dbModel = DbSQLModel( *a, **kw, dbType=type(self) )
        dbModel.postAll( self.records )
        return dbModel


class DbSQLModel:

    def __init__(self, url='sqlite:///:memory:', dbType=Db, **kw ):
        self.engine = self._initEngine( url )
        self.dbType = dbType
        
    @classmethod
    def _initEngine( cls, url, **kw ):
        if ':memory:' in url:
            engine = create_engine( url, **kw )
            SQLModel.metadata.create_all( engine )
            return engine

    def post( self, obj, name=None ):
        model = self._post( obj, name=name )

        with Session( self.engine ) as session:
            sqlModel = model.asSQLModel()

            session.add( sqlModel )
            session.commit()
            self._refreshWithSession( session, sqlModel )

            return sqlModel

    def _post( self, obj, name=None ):
        return self.dbType._post( obj, name=name )

    def postAll( self, objs ):
        models    = [ self._post( o ) for o in objs ]
        sqlModels = [ model.asSQLModel() for model in models ]

        with Session( self.engine ) as session:

            session.add_all( sqlModels )
            session.commit()
            
            for sqlModel in sqlModels:
                self._refreshWithSession( session, sqlModel )

            return sqlModels

    def getAll( self ):
        query = self._makeQuery( 
            select( record.RecordSQLModel ) 
        )
        with Session( self.engine ) as session:                
            results = session.exec( query ).all()
            return results

    def getByName( self, name ):
        query = self._makeNameQuery( name )
        return self._get( query )

    def getById( self, id ):
        query = self._makeIdQuery( id )
        return self._get( query )

    def _get( self, query ):
        with Session( self.engine ) as session:
            result = session.exec( query ).one_or_none()
            return result

    def deleteByName( self, name ):
        query = self._makeNameQuery( name )
        return self._delete( query )

    def deleteById( self, id ):
        query = self._makeIdQuery( id )
        return self._delete( query )

    def put( self, obj, name=None ):
        """
        Put (update or create) a record atomically.
        
        If a record with the given name exists, it is replaced.
        If it doesn't exist, a new record is created.
        This is idempotent - calling put() multiple times with the same
        name results in the same state.
        
        The operation is atomic: both delete and post happen within
        a single database transaction. If either fails, the transaction
        is rolled back and the database state remains unchanged.
        """
        # Prepare the new record model first (validate before transaction)
        model = self._post( obj, name=name )
        
        # Use a single transaction for both delete and post
        with Session( self.engine ) as session:
            try:
                # Delete existing record if it exists
                query    = self._makeNameQuery( name )
                sqlModel = session.exec( query ).one_or_none()

                if sqlModel:
                    self._deleteWithSession( session, sqlModel )
                    session.flush() # Flush to ensure delete is processed before insert
                
                # Add the new record
                sqlModelNew = model.asSQLModel()
                session.add( sqlModelNew )
                
                # Commit both operations together
                session.commit()
                self._refreshWithSession( session, sqlModelNew )
                
                return sqlModelNew

            except Exception:
                session.rollback() # Rollback the entire transaction on any error
                raise

    @staticmethod
    def _refreshWithSession( session, sqlModel ):
        """ Refresh to get generated ids, including nested relationships """
        session.refresh( sqlModel )
        session.refresh( sqlModel.info )
        session.refresh( sqlModel.body )

    def _delete( self, query ):
        with Session( self.engine ) as session:
            sqlModel = session.exec( query ).one_or_none()
            if sqlModel:
                self._deleteWithSession( session, sqlModel )
                session.commit()
                return True
            return False

    @staticmethod
    def _deleteWithSession( session, sqlModel ):
        """ Delete related objects first, then the record """
        session.delete( sqlModel.info )
        session.delete( sqlModel.body )
        session.delete( sqlModel )

    @classmethod
    def _makeNameQuery( cls, name ):
        return cls._makeQuery( 
            select( record.RecordSQLModel )
            .join( info.InfoSQLModel )
            .where( info.InfoSQLModel.name == name )
        )
            
    @classmethod
    def _makeIdQuery( cls, id ):
        return cls._makeQuery( 
            select( record.RecordSQLModel )
            .where( record.RecordSQLModel.id == id ) 
        )

    @staticmethod
    def _makeQuery( query ):
        return (
            query
            .options( selectinload( record.RecordSQLModel.info ) )
            .options( selectinload( record.RecordSQLModel.body ) )
        )

    def asModel( self ):
        return self.dbType( records=[ rec.asModel() for rec in self.getAll() ] )
    