from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.orm import selectinload
from typing import ClassVar
from functools import singledispatchmethod
from pydantic import Field
from pyswark.lib.pydantic import base

from pyswark.core.models import mixin, record, body, info


class Db( base.BaseModel, mixin.TypeCheck ):
    """Base class for a database."""
    Record  : ClassVar[ type ] = record.Record
    records : list[ record.Record ] = Field( default_factory=list )

    def post( self, obj, name=None ):
        rec = self._post( obj, name=name )
        self.records.append( rec )
        return rec

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
    def _post_body( cls, bod: body.Body, name ):
        """Post a Body directly."""
        rec = cls.Record( info={ 'name': name }, body=bod )
        return cls._post_after( rec )

    @_post.register( base.BaseModel )
    @classmethod
    def _post_model( cls, model: base.BaseModel, name=None ):
        """Post a BaseModel (wraps in a Record)."""
        if not name:
            raise ValueError( f"name is required for type={ type(model) }" )
        rec = cls.Record( info={ 'name': name }, body={ 'model': model } )
        return cls._post_after( rec )

    @classmethod
    def _post_after( cls, rec: record.Record ):
        """Validate the record and return it."""
        cls.checkIfInstance( rec, cls.Record )
        return rec

    def getByName( self, name ):
        sqlModel = self.asSQLModel()
        result   = sqlModel.getByName( name )
        return result if result is None else result.asModel()

    def deleteByName( self, name ):
        sqlModel     = self.asSQLModel()
        success      = sqlModel.deleteByName( name )
        self.records = sqlModel.asModel().records
        return success

    def asSQLModel( self, *a, **kw ):
        dbModel = DbSQLModel( *a, **kw )
        dbModel.postAll( self.records )
        return dbModel


class DbSQLModel( mixin.TypeCheck ):
    RecordType : ClassVar[ str ] = record.RecordSQLModel.getUri()
    DbType     : ClassVar[ str ] = Db.getUri()

    def __init__(self, url='sqlite:///:memory:', **kw ):
        self.engine = self._initEngine( url )

        self._recordType = self.importType( self.RecordType )
        self._dbType     = self.importType( self.DbType )
        
    @classmethod
    def _initEngine( cls, url, **kw ):
        if ':memory:' in url:
            cls.importType( cls.RecordType ) # import SQL Models
            engine = create_engine( url, **kw )
            SQLModel.metadata.create_all( engine )
            return engine

    def post( self, obj, name=None ):
        model = self._dbType._post( obj, name=name )

        with Session( self.engine ) as session:
            sqlModel = model.asSQLModel()

            session.add( sqlModel )
            session.commit()
            
            # Refresh to get generated ids, including nested relationships
            session.refresh( sqlModel )
            session.refresh( sqlModel.info )
            session.refresh( sqlModel.body )

            return sqlModel

    def postAll( self, objs ):
        models    = [ self._dbType._post( o ) for o in objs ]
        sqlModels = [ model.asSQLModel() for model in models ]

        with Session( self.engine ) as session:

            session.add_all( sqlModels )
            session.commit()
            
            # Refresh all to load relationships before session closes
            for sqlModel in sqlModels:
                session.refresh( sqlModel )
                session.refresh( sqlModel.info )
                session.refresh( sqlModel.body )

            return sqlModels

    def getAll( self ):
        stmt = self._statement( select( self._recordType ) )
        with Session( self.engine ) as session:                
            results = session.exec( stmt ).all()
            return results

    def getByName( self, name ):
        return self._get(
            select( self._recordType )
            .join( info.InfoSQLModel )
            .where( info.InfoSQLModel.name == name )
        )

    def getById( self, id ):
        return self._get(
            select( self._recordType )
            .where( self._recordType.id == id )
        )

    def _get( self, query ):
        stmt = self._statement( query )
        with Session( self.engine ) as session:
            result = session.exec( stmt ).one_or_none()
            return result

    def deleteByName( self, name ):
        return self._delete(
            select( self._recordType )
            .join( info.InfoSQLModel )
            .where( info.InfoSQLModel.name == name )
        )

    def deleteById( self, id ):
        return self._delete(
            select( self._recordType )
            .where( self._recordType.id == id )
        )

    def _delete( self, query ):
        stmt = self._statement( query )
        with Session( self.engine ) as session:
            result = session.exec( stmt ).one_or_none()
            if result:
                # Delete related objects first, then the record
                session.delete( result.info )
                session.delete( result.body )
                session.delete( result )
                session.commit()
                return True
            return False

    def _statement( self, query ):
        return (
            query
            .options( selectinload( self._recordType.info ) )
            .options( selectinload( self._recordType.body ) )
        )

    def asModel( self ):
        return self._dbType( records=[ rec.asModel() for rec in self.getAll() ] )
    