from pathlib import Path
from pyswark.lib.pydantic import base
from pyswark.core import extractor
from pyswark.core.io import api
from pyswark.core.models import db

from pyswark.gluedb.models import IoModel


class Db( db.Db ):
    AllowedInstances = [ IoModel, base.BaseModel ]

    @classmethod
    def _post_fallback( cls, obj, name=None ):
        _, obj, name = cls._post_fallback_ioModel( obj, name=name )
        return obj, name

    @classmethod
    def _post_fallback_ioModel( cls, obj, name=None, success=False ):
        success, obj, name = cls._post_fallback_uri( obj, name )

        if success:
            if isinstance( obj, dict ):
                name = obj.get( 'name', name )
                obj = IoModel( **obj )
            elif isinstance( obj, (list, tuple) ):
                obj = IoModel.fromArgs( *obj )

        return success, obj, name

    @classmethod
    def _post_fallback_uri( cls, obj, name=None, success=False ):

        if isinstance( obj, Path ):
            obj = str( obj )

        if isinstance( obj, str ):
            if api.isUri( obj ):
                obj = { 'uri' : str( obj ) }
                success = True
            else:
                try:
                    obj = api.read( obj, datahandler='string' )
                    success = True
                except:
                    success = False

        return success, obj, name

    def extract( self, name ):        
        record = self.getByName( name )
        model = self._handle( record, IoModel.extract )

        if isinstance( model, extractor.Extractor ):
            return model.extract()

        return model

    def load( self, data, name ):
        record = self.getByName( name )
        return self._handle( record, IoModel.load, data )

    def acquireExtract( self, name ):
        record = self.getByName( name )
        return self._handle( record, IoModel.acquireExtract )

    def acquireLoad( self, name ):
        record = self.getByName( name )
        return self._handle( record, IoModel.acquireLoad )

    def _handle( self, record, method, *args, **kwargs ):
        model = record.acquire()
        
        if isinstance( model, IoModel ):
            return method( model, *args, **kwargs )

        return model

    def get( self, name ):
        """
        Get a record by name (alias for getByName).
        
        Parameters
        ----------
        name : str
            The name of the record to retrieve.
        
        Returns
        -------
        Record
            The record with the given name, or None if not found.
        """
        return self.getByName( name )

    def delete( self, name ):
        """
        Delete a record by name (alias for deleteByName).
        
        Parameters
        ----------
        name : str
            The name of the record to delete.
        
        Returns
        -------
        bool
            True if the record was deleted, False if it didn't exist.
        """
        return self.deleteByName( name )

    def getNames( self ):
        """
        Get all record names in the database.
        
        Returns
        -------
        list[str]
            List of all record names.
        """
        return [ rec.info.name for rec in self.records ]

    def __contains__( self, name ):
        """
        Check if a record with the given name exists in the database.
        
        This checks the in-memory records list first (fast), then the SQL
        database if needed. The in-memory list is the source of truth for
        records that have been posted but not yet synced to SQL.
        
        Parameters
        ----------
        name : str
            The name to check for.
        
        Returns
        -------
        bool
            True if a record with that name exists, False otherwise.
        """
        try:
            sqlModel = self.asSQLModel()
            return sqlModel.getByName( name ) is not None
        except Exception:
            # If check fails, assume not present
            return False

    def merge( self, other ):
        """
        Merge records from another database into this one.
        
        Parameters
        ----------
        other : Db
            Another GlueDb instance to merge from.
        
        Example
        -------
        >>> db1.merge(db2)  # Adds all records from db2 to db1
        """
        if not isinstance( other, db.Db ):
            raise TypeError( f"can only merge type Db, got type={type(other)}" )
        self.records.extend( other.records )
