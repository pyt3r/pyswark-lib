from pathlib import Path
from typing import ClassVar
from pyswark.lib.pydantic import base

from pyswark.core import extractor
from pyswark.core.io import api
from pyswark.core.models import db

from pyswark.gluedb.models import iomodel


class Base( db.Db ):

    def getNames( self ):
        """
        Get all record names in the database.
        
        Returns
        -------
        list[str]
            List of all record names.
        """
        return [ rec.info.name for rec in self.records ]

    def acquire( self, name ):
        return self.get( name ).acquire()

    def extract( self, name ):
        return self.acquire( name ).extract()

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
        tmp = Db().postAll( self.records )
        self.records = tmp.records
        


class Db( Base ):
    """
    GlueDb - A database of named records pointing to data sources.
    
    A GlueDb is a collection of named records, where each record can point to
    a data source via URI or contain inline data. Records can be extracted,
    loaded, and managed through a simple API.
    
    Key Features
    -----------
    - Store records by name with URI or inline data
    - Extract data from records automatically
    - Merge multiple databases together
    - Serialize to/from .gluedb files
    
    Example
    -------
    >>> from pyswark.gluedb import db
    >>> 
    >>> # Create a new database
    >>> db = db.Db()
    >>> 
    >>> # Post records
    >>> db.post('prices', 'file:./prices.csv')
    >>> db.post('config', {'window': 60})
    >>> 
    >>> # Extract data
    >>> prices = db.extract('prices')
    >>> 
    >>> # List all names
    >>> print(db.getNames())  # ['prices', 'config']
    """
    IOMODEL: ClassVar = iomodel.IoModel
    AllowedInstances = [ IOMODEL, base.BaseModel ]

    @classmethod
    def _post_fallback( cls, obj, name=None ):
        _, obj, name = cls._post_fallback_ioModel( obj, name=name )
        return obj, name

    @classmethod
    def _post_fallback_ioModel( cls, obj, name=None, success=False ):
        _, obj, name = cls._post_fallback_uri( obj, name )

        if isinstance( obj, dict ):
            name = obj.get( 'name', name )
            obj = cls.IOMODEL( **obj )

        elif isinstance( obj, (list, tuple) ):
            obj = cls.IOMODEL.fromArgs( *obj )

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
                    obj = api.read( obj, datahandler='string' ) # json to dict 
                    success = True
                except:
                    success = False

        return success, obj, name

    def extract( self, name ):
        """
        Extract data from a record by name.
        
        This method retrieves the record and extracts its data. If the record
        points to a URI, the data will be loaded from that URI. If the record
        contains inline data, it will be returned directly.
        
        Parameters
        ----------
        name : str
            The name of the record to extract.
        
        Returns
        -------
        Any
            The extracted data (type depends on the record's data source).
        
        Example
        -------
        >>> db.post('prices', 'file:./prices.csv')
        >>> prices_df = db.extract('prices')
        """
        record = self.get( name )
        model = self._handle( record, self.IOMODEL.extract )

        if isinstance( model, extractor.Extractor ):
            return model.extract()

        return model

    def load( self, data, name ):
        record = self.get( name )
        return self._handle( record, self.IOMODEL.load, data )

    def acquireExtract( self, name ):
        record = self.get( name )
        return self._handle( record, self.IOMODEL.acquireExtract )

    def acquireLoad( self, name ):
        record = self.get( name )
        return self._handle( record, self.IOMODEL.acquireLoad )

    def _handle( self, record, method, *args, **kwargs ):
        model = record.acquire()
        
        if isinstance( model, self.IOMODEL ):
            return method( model, *args, **kwargs )

        return model
