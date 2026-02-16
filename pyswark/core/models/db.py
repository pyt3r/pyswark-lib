import enum as _enum
from functools import singledispatchmethod

from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.orm import selectinload
from typing import ClassVar, Union
from pydantic import Field
from pyswark.lib.pydantic import base
from pyswark.lib import enum

from pyswark.core.models import mixin, record, body, info


class MixinName:

    @staticmethod
    def _processName( name ):
        if isinstance( name, _enum.Enum ):
            name = name.name
        return name


class MixinDb( base.BaseModel, MixinName ):
    """Base class for a database."""
    AllowedTypes     : ClassVar[ list[ Union[ str, type ] ] ] = []
    AllowedInstances : ClassVar[ list[ Union[ str, type ] ] ] = []

    records     : list[ record.Record ] = Field( default_factory=list )
    url         : str                   = Field( default='', description="URI to db file" )
    datahandler : str                   = Field( default='pjson', description="Datahandler to use for loading and persisting" )
    engine_url  : str                   = Field( default='sqlite:///:memory:', description="SQLModel engine URL" )
    persist     : bool                  = Field( default=False, description="Persist to .file on context exit" )

    @classmethod
    def connect( cls, url, datahandler='', persist=False ):
        """
        Connect to a .gluedb (load if exists), use engine_url for SQLModel,
        and optionally persist to the .gluedb file on context exit.

        Parameters
        ----------
        url : str
            URI to a ``db`` file (e.g. ``file:./data.gluedb`` or
            ``pyswark:/data/catalog.gluedb``). If it exists, records are loaded.
            If None, no load or persist is done.
        persist : bool, optional
            If True and url is set, write self to url on successful
            context exit. Default False.

        Returns
        -------
        Db
            An instance usable as a context manager. Use ``with Db.connect(...) as db:``.

        Example
        -------
        >>> with Db.connect('file:./catalog.gluedb', persist=True) as db:
        ...     db.post(ticker, name='AAPL')
        ...     # On exit: writes to file:./catalog.gluedb
        ...
        >>> with Db.connect('file:./catalog.gluedb', engine_url='sqlite:///:memory:') as db:
        ...     # Loaded from .gluedb; SQL runs in memory; no persist
        ...     db.getByName('AAPL')
        """
        from pyswark.core.io import api

        o = cls( url=url, datahandler=datahandler, persist=persist )

        loaded = api.read( o.url, datahandler=o.datahandler )

        if isinstance( loaded, cls ):
            loaded.url         = o.url
            loaded.datahandler = o.datahandler
            loaded.persist     = o.persist

            o = loaded

        else:
            raise ValueError( f"Expected type={ cls }, got type={ type(loaded) } from url={ o.url }" )

        return o

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.persistToFile()

        return False

    def persistToFile( self ):
        if self.persist and self.url:

            from pyswark.core.io import api
            api.write( self, self.url, datahandler=self.datahandler, overwrite=True )

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
        try:
            sqlModel.postAll( objs )
            self.records = sqlModel.asModel().records
            return self
        finally:
            sqlModel.dispose()

    def post( self, obj, name=None, **infoKw ):
        name  = self._processName( name )
        dbModel = self.asSQLModel()
        try:
            model = dbModel.post( obj, name=name )
            self.records.append( model )
            return model
        finally:
            dbModel.dispose()

    def getByName( self, name ):
        name = self._processName( name )
        sqlModel = self.asSQLModel()
        try:
            return sqlModel.getByName( name )
        finally:
            sqlModel.dispose()

    def deleteByName( self, name ):
        name = self._processName( name )
        sqlModel = self.asSQLModel()
        try:
            success = sqlModel.deleteByName( name )
            self.records = sqlModel.asModel().records
            return success
        finally:
            sqlModel.dispose()

    def put( self, obj, name=None ):
        dbModel = self.asSQLModel()
        try:
            model = dbModel.put( obj, name=name )
            self.records = dbModel.asModel().records
            return model
        finally:
            dbModel.dispose()

    def __contains__( self, name ):
        name = self._processName( name )
        sqlModel = self.asSQLModel()
        try:
            return name in sqlModel
        finally:
            sqlModel.dispose()

    def asSQLModel( self, url=None, **kw ):
        url = url or self.engine_url
        dbModel = DbSQLModel( url=url, **kw, dbType=type(self) )
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


class Db( MixinDb, MixinPost ):
    AllowedTypes     : ClassVar[ list[ Union[ str, type ] ] ] = []
    AllowedInstances : ClassVar[ list[ Union[ str, type ] ] ] = []


class MixinConnect:
    """Mixin providing context manager functionality for database connections."""

    @classmethod
    def connect( cls, url, dbType=Db, **kw ):
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
            self.dispose()
        
        return False  # Don't suppress exceptions
    
    def _get_session(self):
        """Get the current session, returning None if not in context manager."""
        if self._in_context and self._session is not None:
            return self._session
        # Not in context manager - return None to use with Session() pattern
        return None

    def dispose(self):
        """Release the engine and its connection pool. No-op in base; override in DbSQLModel."""
        pass
    
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


class DbSQLModel( MixinConnect, MixinName ):
    INFO   = info.InfoSQLModel
    BODY   = body.BodySQLModel
    RECORD = record.RecordSQLModel
 
    def __init__(self, url, dbType=Db, **kw ):
        self.engine = self._initEngine( url )
        self.dbType = dbType
        super().__init__()  # Initialize MixinConnect

    def dispose(self):
        """Close the engine and its connection pool. Idempotent."""
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
        
    @classmethod
    def _initEngine( cls, url, **kw ):
        engine = create_engine( url, **kw )
        SQLModel.metadata.create_all( engine )
        return engine

    def _with_session( self, fn, *, commit=True ):
        """
        Run fn(session). If we have an active context-manager session, use it
        (no commit). Otherwise create a new Session, run fn, and commit on success.
        On exception in the new-session case, rollback and re-raise.
        """
        session = self._get_session()
        if session is not None:
            return fn( session )
        with Session( self.engine ) as session:
            try:
                result = fn( session )
                if commit:
                    session.commit()
                return result
            except Exception:
                session.rollback()
                raise

    def post( self, obj, name=None, **infokw ):
        name = self._processName( name )
        model = self._post( obj, name=name, **infokw )

        def op( session ):
            sqlModel = model.asSQLModel()
            session.add( sqlModel )
            session.flush()
            self._refreshWithSession( session, sqlModel )
            return sqlModel.asModel()

        return self._with_session( op )

    def _post( self, obj, name=None, **infokw ):
        name = self._processName( name )
        return self.dbType._post( obj, name=name, **infokw )

    def postAll( self, objs ):
        models    = [ self._post( o ) for o in objs ]
        sqlModels = [ model.asSQLModel() for model in models ]

        def op( session ):
            session.add_all( sqlModels )
            session.flush()
            for sqlModel in sqlModels:
                self._refreshWithSession( session, sqlModel )
            return [ m.asModel() for m in sqlModels ]

        return self._with_session( op )

    def getAll( self ):
        query = self._makeQuery( select( self.RECORD ) )

        def op( session ):
            return [ r.asModel() for r in session.exec( query ).all() ]

        return self._with_session( op, commit=False )

    def getByName( self, name ):
        name = self._processName( name )
        query = self._makeNameQuery( name )
        return self._get( query )

    def getById( self, id ):
        query = self._makeIdQuery( id )
        return self._get( query )

    def _get( self, query ):

        def op( session ):
            r = session.exec( query ).one_or_none()
            return r.asModel() if r is not None else None

        return self._with_session( op, commit=False )

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
        name  = self._processName( name )
        model = self._post( obj, name=name )

        def op( session ):
            query    = self._makeNameQuery( name )
            sqlModel = session.exec( query ).one_or_none()
            if sqlModel:
                self._deleteWithSession( session, sqlModel )
                session.flush()
            sqlModelNew = model.asSQLModel()
            session.add( sqlModelNew )
            session.flush()
            self._refreshWithSession( session, sqlModelNew )
            return sqlModelNew.asModel()

        return self._with_session( op )

    @staticmethod
    def _refreshWithSession( session, sqlModel ):
        """ Refresh to get generated ids, including nested relationships """
        session.refresh( sqlModel )
        session.refresh( sqlModel.info )
        session.refresh( sqlModel.body )

    def _delete( self, query ):

        def op( session ):
            sqlModel = session.exec( query ).one_or_none()
            if sqlModel:
                self._deleteWithSession( session, sqlModel )
                return True
            return False

        return self._with_session( op )

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
            .join( cls.RECORD.info )
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
        return self.dbType( records=self.getAll() )
    