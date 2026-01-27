import enum as _enum
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.orm import selectinload
from typing import ClassVar, Union
from functools import singledispatchmethod

from pydantic import Field
from pyswark.lib.pydantic import base
from pyswark.lib import enum

from pyswark.core.models import mixin, record, body, info


class MixinName:

    @staticmethod
    def _processName( name ):
        if isinstance( name, _enum.Enum ):
            return name.value
        return name


class MixinDb( base.BaseModel, MixinName ):
    """Base class for a database."""
    AllowedTypes     : ClassVar[ list[ Union[ str, type ] ] ] = []
    AllowedInstances : ClassVar[ list[ Union[ str, type ] ] ] = []

    records : list[ record.Record ] = Field( default_factory=list )

    @classmethod
    def _post( cls, obj, name=None, **infoKw ):
        try:
            return super()._post( obj, name=name, **infoKw ) # parent's dispatched handlers
        except NotImplementedError:
            obj, name = cls._post_fallback( obj, name=name, **infoKw )
            return super()._post( obj, name=name, **infoKw )

    @property
    def enum(self):
        return enum.Enum.createDynamically({ n: n for n in self.getNames() })

    def postAll( self, objs ):
        sqlModel = self.asSQLModel()
        sqlModel.postAll( objs )
        self.records = sqlModel.asModel().records
        return self

    def post( self, obj, name=None, **infoKw ):
        name = self._processName( name )
        dbModel = self.asSQLModel()
        rec = dbModel.post( obj, name=name )
        model = rec.asModel()
        self.records.append( model )
        return model

    def getByName( self, name ): 
        name = self._processName( name )
        sqlModel = self.asSQLModel()
        result   = sqlModel.getByName( name )
        return result if result is None else result.asModel()

    def deleteByName( self, name ):
        name = self._processName( name )
        sqlModel     = self.asSQLModel()
        success      = sqlModel.deleteByName( name )
        self.records = sqlModel.asModel().records
        return success

    def put( self, obj, name=None ):    
        dbModel = self.asSQLModel()
        sqlModel = dbModel.put( obj, name=name )
        self.records = dbModel.asModel().records
        return sqlModel.asModel()

    def __contains__( self, name ):
        name = self._processName( name )
        sqlModel = self.asSQLModel()
        return name in sqlModel

    def asSQLModel( self, *a, **kw ):
        dbModel = DbSQLModel( *a, **kw, dbType=type(self) )
        dbModel.postAll( self.records )
        return dbModel


class MixinPost( mixin.TypeCheck ):

    @classmethod
    def _post_fallback( cls, obj, name=None, **infoKw ):
        cls._raise( obj, name, **infoKw )

    @classmethod
    def _raise( cls, obj, name, **infoKw ):
        raise NotImplementedError( f"post() not implemented for type { type(obj) } (name='{ name })'" )

    @singledispatchmethod
    @classmethod
    def _post( cls, obj, name=None, **infoKw ):
        """Post an object to the database. Dispatches based on type."""
        cls._raise( obj, name )

    @_post.register( record.Record )
    @classmethod
    def _post_record( cls, rec: record.Record, name=None, **infoKw ):
        """Post a Record directly."""
        if name:
            infoKw['name'] = name
            
        if infoKw:
            rec.info = rec.info.clone( **infoKw )

        return cls._post_after( rec )

    @_post.register( body.Body )
    @classmethod
    def _post_body( cls, bod: body.Body, name=None, **infoKw ):
        """Post a Body directly."""
        if name is None:
            raise ValueError( f"name is required for type={ type(bod) }" )
        infoKw['name'] = name
        rec = record.Record( info=infoKw, body=bod )
        return cls._post_after( rec )

    @_post.register( base.BaseModel )
    @classmethod
    def _post_model( cls, model: base.BaseModel, name=None, **infoKw ):
        """Post a BaseModel (wraps in a Record)."""
        if not name:
            raise ValueError( f"name is required for type={ type(model) }" )
        infoKw['name'] = name
        rec = record.Record( info=infoKw, body={ 'model': model } )
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


class MixinConnect:
    """Mixin providing context manager functionality for database connections."""
    
    def __init__(self, *args, **kwargs):
        """Initialize context manager state."""
        super().__init__(*args, **kwargs)
        self._session = None  # Track active session when used as context manager
        self._in_context = False  # Track if we're in a context manager
    
    def __enter__(self):
        """Enter context manager - create and store session."""
        if self._session is not None:
            raise RuntimeError("Already in a context manager")
        self._session = Session(self.engine)
        self._in_context = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - commit or rollback, then close session."""
        if self._session is None:
            return False
        
        try:
            if exc_type is None:
                # Success - commit changes
                self._session.commit()
            else:
                # Exception occurred - rollback
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None
            self._in_context = False
        
        return False  # Don't suppress exceptions
    
    def _get_session(self):
        """Get the current session, returning None if not in context manager."""
        if self._in_context and self._session is not None:
            return self._session
        # Not in context manager - return None to use with Session() pattern
        return None
    
    def commit(self):
        """Explicitly commit the current transaction."""
        session = self._get_session()
        if session is None:
            raise RuntimeError("commit() can only be called within a context manager")
        session.commit()
    
    def rollback(self):
        """Explicitly rollback the current transaction."""
        session = self._get_session()
        if session is None:
            raise RuntimeError("rollback() can only be called within a context manager")
        session.rollback()


class Db( MixinDb, MixinPost ):
    AllowedTypes     : ClassVar[ list[ Union[ str, type ] ] ] = []
    AllowedInstances : ClassVar[ list[ Union[ str, type ] ] ] = []


class DbSQLModel( MixinConnect, MixinName ):
    INFO   = info.InfoSQLModel
    BODY   = body.BodySQLModel
    RECORD = record.RecordSQLModel
 
    def __init__(self, url='sqlite:///:memory:', dbType=Db, **kw ):
        self.engine = self._initEngine( url )
        self.dbType = dbType
        super().__init__()  # Initialize MixinConnect
    
    @classmethod
    def connect(cls, url='sqlite:///:memory:', dbType=Db, **kw):
        """
        Connect to a database and return a context manager.
        
        Parameters
        ----------
        url : str, optional
            Database URL. Defaults to in-memory SQLite.
            Examples:
            - 'sqlite:///:memory:' (in-memory, default)
            - 'sqlite:///./mydb.db' (file-based, relative path)
            - 'sqlite:////absolute/path/to/db.db' (absolute path)
        dbType : type, optional
            The Db class to use. Defaults to Db.
        **kw
            Additional arguments passed to create_engine().
            
        Returns
        -------
        DbSQLModel
            A DbSQLModel instance that can be used as a context manager.
            
        Example
        -------
        >>> # File-based database with auto-commit
        >>> with DbSQLModel.connect('sqlite:///./data.db') as db:
        ...     db.post(ticker, name='AAPL')
        ...     # Auto-commits on successful exit
        ...
        >>> # In-memory database (default)
        >>> with DbSQLModel.connect() as db:
        ...     db.post(ticker, name='AAPL')
        """
        instance = cls(url=url, dbType=dbType, **kw)
        return instance
        
    @classmethod
    def _initEngine( cls, url, **kw ):
        engine = create_engine( url, **kw )
        SQLModel.metadata.create_all( engine )
        return engine

    def post( self, obj, name=None, **infokw ):
        name = self._processName( name )
        model = self._post( obj, name=name, **infokw )

        session = self._get_session()
        if session is not None:
            # In context manager - use existing session
            sqlModel = model.asSQLModel()
            session.add( sqlModel )
            session.flush()  # Flush to make object persistent so we can refresh
            # Don't commit here - let context manager handle it
            self._refreshWithSession( session, sqlModel )
            return sqlModel
        else:
            # Not in context manager - create new session (backward compatible)
            with Session( self.engine ) as session:
                sqlModel = model.asSQLModel()
                session.add( sqlModel )
                session.commit()
                self._refreshWithSession( session, sqlModel )
                return sqlModel

    def _post( self, obj, name=None, **infokw ):
        name = self._processName( name )
        return self.dbType._post( obj, name=name, **infokw )

    def postAll( self, objs ):
        models    = [ self._post( o ) for o in objs ]
        sqlModels = [ model.asSQLModel() for model in models ]

        session = self._get_session()
        if session is not None:
            # In context manager - use existing session
            session.add_all( sqlModels )
            session.flush()  # Flush to make objects persistent so we can refresh
            # Don't commit here - let context manager handle it
            for sqlModel in sqlModels:
                self._refreshWithSession( session, sqlModel )
            return sqlModels
        else:
            # Not in context manager - create new session (backward compatible)
            with Session( self.engine ) as session:
                session.add_all( sqlModels )
                session.commit()
                for sqlModel in sqlModels:
                    self._refreshWithSession( session, sqlModel )
                return sqlModels

    def getAll( self ):
        query = self._makeQuery( 
            select( self.RECORD ) 
        )
        session = self._get_session()
        if session is not None:
            # In context manager - use existing session
            return session.exec( query ).all()
        else:
            # Not in context manager - create new session (backward compatible)
            with Session( self.engine ) as session:                
                return session.exec( query ).all()

    def getByName( self, name ):
        name = self._processName( name )
        query = self._makeNameQuery( name )
        return self._get( query )

    def getById( self, id ):
        query = self._makeIdQuery( id )
        return self._get( query )

    def _get( self, query ):
        session = self._get_session()
        if session is not None:
            # In context manager - use existing session
            return session.exec( query ).one_or_none()
        else:
            # Not in context manager - create new session (backward compatible)
            with Session( self.engine ) as session:
                return session.exec( query ).one_or_none()

    def deleteByName( self, name ):
        name = self._processName( name )
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
        name = self._processName( name )
        model = self._post( obj, name=name )
        
        session = self._get_session()
        if session is not None:
            # In context manager - use existing session
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
                session.flush()  # Flush to make object persistent so we can refresh
                # Don't commit here - let context manager handle it
                self._refreshWithSession( session, sqlModelNew )
                
                return sqlModelNew

            except Exception:
                session.rollback() # Rollback the entire transaction on any error
                raise
        else:
            # Not in context manager - create new session (backward compatible)
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
        session = self._get_session()
        if session is not None:
            # In context manager - use existing session
            sqlModel = session.exec( query ).one_or_none()
            if sqlModel:
                self._deleteWithSession( session, sqlModel )
                # Don't commit here - let context manager handle it
                return True
            return False
        else:
            # Not in context manager - create new session (backward compatible)
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
            select( cls.RECORD )
            .join( cls.INFO )
            .where( cls.INFO.name == name )
        )
            
    @classmethod
    def _makeIdQuery( cls, id ):
        return cls._makeQuery( 
            select( cls.RECORD )
            .where( cls.RECORD.id == id ) 
        )

    @classmethod
    def _makeQuery( cls, query ):
        return (
            query
            .options( selectinload( cls.RECORD.info ) )
            .options( selectinload( cls.RECORD.body ) )
        )

    def __contains__( self, name ):
        name = self._processName( name )
        return self.getByName( name ) is not None

    def asModel( self ):
        return self.dbType( records=[ rec.asModel() for rec in self.getAll() ] )
    