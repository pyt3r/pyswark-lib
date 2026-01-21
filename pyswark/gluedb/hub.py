"""
GlueHub - Collection of GlueDb Instances
=========================================

A GlueHub is a container for multiple GlueDb instances, allowing you to
organize and manage related databases together.

Example
-------
>>> from pyswark.gluedb import api
>>>
>>> # Create a hub
>>> hub = api.newHub()
>>> hub.post('market_data', market_db)
>>> hub.post('config', config_db)
>>>
>>> # Extract a database from the hub
>>> market_db = hub.extract('market_data')
>>>
>>> # Consolidate all databases into one
>>> consolidated = hub.toDb()
"""

from typing import Union
from pyswark.lib.pydantic import base
from pyswark.gluedb import db


class Contents(base.BaseModel):
    """
    Contents model for GlueHub records.
    
    Stores a reference to a GlueDb instance, either as a URI string
    or as a Db instance directly.
    """
    
    gluedb: Union[str, db.Db]
    
    def extract(self):
        """
        Extract the GlueDb instance from this contents.
        
        If gluedb is a string URI, it will be loaded using api.connect().
        If it's already a Db instance, it will be returned directly.
        
        Returns
        -------
        Db
            The GlueDb instance.
        """
        gluedb = self.gluedb
        
        if isinstance(gluedb, str):
            # Import locally to avoid circular import
            from pyswark.gluedb.api import connect
            gluedb = connect(gluedb)
        
        # Check for GlueHub using string to avoid forward reference
        if type(gluedb).__name__ == 'GlueHub':
            raise TypeError(f"Expected type=Db, got type=GlueHub")
        
        if not isinstance(gluedb, db.Db):
            raise TypeError(f"Expected type=Db, got type={type(gluedb)}")
        
        return gluedb


class GlueHub(db.Db):
    """
    A hub containing multiple GlueDb instances.
    
    GlueHub extends Db but uses Contents model to store references to
    other GlueDb instances. This allows organizing multiple databases
    together and consolidating them when needed.
    
    Example
    -------
    >>> hub = api.newHub()
    >>> hub.post('market_data', market_db)
    >>> hub.post('config', 'pyswark:/data/config.gluedb')
    >>> 
    >>> # Extract a database
    >>> market_db = hub.extract('market_data')
    >>> 
    >>> # Consolidate all databases
    >>> consolidated = hub.toDb()
    """
    
    AllowedInstances = [Contents, base.BaseModel]
    
    @classmethod
    def _post(cls, obj, name=None):
        """
        Post an object to the hub.
        
        Handles:
        - Db instances: wrapped in Contents
        - String URIs: converted to Contents with gluedb=uri
        - Dict: converted to Contents
        - Contents: posted directly
        """
        try:
            return super()._post(obj, name=name)  # parent's dispatched handlers
            
        except NotImplementedError:
            
            # Handle Db instances
            if isinstance(obj, db.Db):
                obj = Contents(gluedb=obj)
            
            # Handle string URIs
            elif isinstance(obj, str):
                obj = Contents(gluedb=obj)
            
            # Handle dict
            elif isinstance(obj, dict):
                # If it has 'gluedb' key, assume it's Contents-like
                if 'gluedb' in obj:
                    obj = Contents(**obj)
                else:
                    # Otherwise, try to create Contents with gluedb=obj
                    obj = Contents(gluedb=obj)
            
            return super()._post(obj, name=name)
    
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
