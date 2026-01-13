from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.orm import selectinload
from typing import ClassVar, Union
from functools import singledispatchmethod
from pydantic import field_validator, model_validator, Field
from pyswark.lib.pydantic import base

from pyswark.core.models import mixin, record, body, info


class Db( base.BaseModel, mixin.TypeCheck ):
    """Base class for a database."""
    Record  : ClassVar[ type ] = record.Record
    records : list[ record.Record ] = Field( default_factory=list )

    def post( self, obj, name=None ):
        return self._post( obj, name=name )

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


class DbSQLModel( mixin.TypeCheck ):
    RecordType = record.RecordSQLModel.getUri()
    DbType     = Db.getUri()

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
        models = [ self._dbType._post( o ) for o in objs ]

        with Session( self.engine ) as session:

            sqlModels = [ model.asSQLModel() for model in models ]

            session.add_all( sqlModels )
            session.commit()
            
            # Refresh all to load relationships before session closes
            for sqlModel in sqlModels:
                session.refresh( sqlModel )
                session.refresh( sqlModel.info )
                session.refresh( sqlModel.body )

            return sqlModels

    def getAll( self ):
        with Session( self.engine ) as session:
            stmt = (
                select( self._recordType )
                .options( selectinload( self._recordType.info ) )
                .options( selectinload( self._recordType.body ) )
            )
            results = session.exec( stmt ).all()
            return results

    def getByName( self, name ):
        with Session( self.engine ) as session:
            stmt = (
                select( self._recordType )
                .join( info.InfoSQLModel )
                .where( info.InfoSQLModel.name == name )
                .options( selectinload( self._recordType.info ) )
                .options( selectinload( self._recordType.body ) )
            )
            result = session.exec( stmt ).one_or_none()
            return result

    def getById( self, id ):
        with Session( self.engine ) as session:
            stmt = (
                select( self._recordType )
                .where( self._recordType.id == id )
                .options( selectinload( self._recordType.info ) )
                .options( selectinload( self._recordType.body ) )
            )
            result = session.exec( stmt ).one_or_none()
            return result