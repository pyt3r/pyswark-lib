"""
Hub - Collection of GlueDb Instances
=========================================

A Hub is a container for multiple GlueDb instances, allowing you to
organize and manage related databases together.

Example
-------
>>> from pyswark.gluedb import hub
>>>
>>> # Create a hub
>>> hub = hub.Hub()
>>> hub.post('market_data', market_db)
>>> hub.post('config', config_db)
>>>
>>> # Extract a database from the hub
>>> market_db = hub.extract('market_data')
>>>
>>> # Consolidate all databases into one
>>> consolidated = hub.toDb()
"""
from pyswark.gluedb import db
from pyswark.gluedb.models import iomodel


class Hub(db.Db):
    """
    A hub containing multiple GlueDb instances.
    
    Hub extends Db but uses Contents model to store references to
    other GlueDb instances. This allows organizing multiple databases
    together and consolidating them when needed.
    
    Example
    -------
    >>> from pyswark.gluedb import hub
    >>> hub = hub.Hub()
    >>> hub.post('market_data', market_db)
    >>> hub.post('config', 'pyswark:/data/config.gluedb')
    >>> 
    >>> # Extract a database
    >>> market_db = hub.extract('market_data')
    >>> 
    >>> # Consolidate all databases
    >>> consolidated = hub.toDb()
    """
    AllowedInstances = [ iomodel.IoModel, db.Base ]
    
    def extract(self, name):
        """
        Extract a database from the hub by name.
        
        This method retrieves the record and extracts its data. If the record
        points to a URI, the data will be loaded from that URI. If the record
        contains inline data, it will be returned directly.
        """
        gluedb = super().extract(name)

        if not isinstance( gluedb, db.Base ):
            raise TypeError( f"Expected type={ db.Base }, got type={ type(gluedb) }" )
        
        return gluedb

    def load(self, data, name):
        """
        Load a database into the hub by name.
        
        This method stores the database in the hub under the given name.
        """
        if not isinstance( data, db.Base ):
            raise TypeError( f"Expected type={ db.Base }, got type={ type(data) }" )

        return super().load(data, name)

    def getFromDb( self, dbName, name ):
        """
        Get a record from the underlying GlueDb without persisting anything.
        """
        _, target_db = self._get_db_and_contents( dbName )
        return target_db.get( name )

    def postToDb( self, obj, dbName, name=None, overwrite=True ):
        """
        Post an entry to the underlying GlueDb and overwrite it to the URI it points to.

        Uses .acquire() and .extract() to get the Db for the given dbName, posts
        the object to that Db, then persists the modified Db back to its URI
        (e.g. the file the gluedb object points to).

        Parameters
        ----------
        obj : Any
            Object to post (e.g. dict, BaseModel, or URI string).
        dbName : str
            Name of the database in the hub to post to.
        name : str, optional
            Record name for the new entry. If None, taken from obj.name or obj['name'] when possible.
        overwrite : bool, optional
            If True (default), allow overwriting the target URI when persisting. Pass False to forbid overwrite.

        Returns
        -------
        Record or None
            The posted record from the target Db, or None.

        Example
        -------
        >>> hub.postToDb(collection.Dict({'x': 1}), 'db_1', name='new_entry')
        """
        contents, target_db = self._get_db_and_contents( dbName )

        entry_name = name
        if entry_name is None:
            entry_name = getattr( obj, 'name', None )
        if entry_name is None and isinstance( obj, dict ):
            entry_name = obj.get( 'name' )
        if entry_name is None:
            raise ValueError( "postToDb requires name= or obj with .name / obj['name']" )
        target_db.post( obj, name=entry_name )
        if hasattr( contents, 'load' ):
            contents.load( target_db, overwrite=overwrite )
        return target_db.get( entry_name )

    def putToDb( self, obj, dbName, name=None, overwrite=True ):
        """
        Put (upsert) an entry into the underlying GlueDb and persist it.

        This mirrors GlueDb.put: if a record with the given name exists it is
        updated, otherwise it is created. After the operation the modified Db
        is written back to the URI it points to.
        """
        contents, target_db = self._get_db_and_contents( dbName )

        entry_name = name
        if entry_name is None:
            entry_name = getattr( obj, 'name', None )
        if entry_name is None and isinstance( obj, dict ):
            entry_name = obj.get( 'name' )
        if entry_name is None:
            raise ValueError( "putToDb requires name= or obj with .name / obj['name']" )

        target_db.put( obj, name=entry_name )
        if hasattr( contents, 'load' ):
            contents.load( target_db, overwrite=overwrite )
        return target_db.get( entry_name )

    def mergeToDb( self, otherDb, dbName, overwrite=True ):
        """
        Merge another GlueDb into a database in the hub and persist it.

        Parameters
        ----------
        otherDb : Db
            Another GlueDb instance whose records will be merged into the
            target database.
        dbName : str
            Name of the database in the hub to merge into.
        overwrite : bool, optional
            If True (default), allow overwriting the target URI when persisting.

        Returns
        -------
        Db
            The merged target GlueDb.
        """
        if not isinstance( otherDb, db.Base ):
            raise TypeError( f"mergeToDb expects otherDb to be a GlueDb, got {type(otherDb)}" )

        contents, target_db = self._get_db_and_contents( dbName )
        target_db.merge( otherDb )
        if hasattr( contents, 'load' ):
            contents.load( target_db, overwrite=overwrite )
        return target_db

    def deleteFromDb( self, dbName, name, overwrite=True ):
        """
        Delete an entry from the underlying GlueDb and persist the change.
        """
        contents, target_db = self._get_db_and_contents( dbName )
        success = target_db.delete( name )
        if success and hasattr( contents, 'load' ):
            contents.load( target_db, overwrite=overwrite )
        return success

    def extractFromDb( self, dbName, name ):
        """
        Extract data from a record in the underlying GlueDb.
        """
        _, target_db = self._get_db_and_contents( dbName )
        return target_db.extract( name )

    def acquireFromDb( self, dbName, name ):
        """
        Acquire the low-level handler for a record in the underlying GlueDb.
        """
        _, target_db = self._get_db_and_contents( dbName )
        return target_db.acquire( name )

    def _get_db_and_contents( self, dbName ):
        """
        Internal helper to resolve a hub entry to its underlying GlueDb
        instance and the original contents object (IoModel or Db).
        """
        contents = self.acquire( dbName )

        if isinstance( contents, db.Base ):
            target_db = contents
        else:
            target_db = contents.extract()

        if not isinstance( target_db, db.Base ):
            raise TypeError( f"Expected Db from hub entry {dbName!r}, got {type(target_db)}" )

        return contents, target_db

    def toDb(self):
        """
        Consolidate all databases in the hub into a single GlueDb.
        
        This merges all databases stored in the hub into one database.
        Useful for flattening the hub structure.
        
        Returns
        -------
        Db
            A new GlueDb instance containing all records from all databases.
        
        Example
        -------
        >>> consolidated = hub.toDb()
        >>> print(consolidated.getNames())  # All names from all databases
        """
        
        new = db.Db()
        for name in self.getNames():
            other = self.extract( name )
            new.merge( other )
        
        return new
