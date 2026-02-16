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
