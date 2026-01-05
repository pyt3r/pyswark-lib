"""
GlueDb API
==========

This module provides the public API for working with GlueDb data catalogs.
A GlueDb is a named collection of data sources that can be versioned,
shared, and serialized as ``.gluedb`` files.

Key Concepts
------------
- **GlueDb**: A database of named records pointing to data sources
- **GlueHub**: A hub containing multiple GlueDb instances
- **Record**: A named entry with URI and extraction settings

Example
-------
>>> from pyswark.gluedb import api
>>>
>>> # Connect to an existing GlueDb
>>> db = api.connect('pyswark:/data/sma-example.gluedb')
>>> print(db.getNames())  # ['JPM', 'BAC', 'kwargs']
>>>
>>> # Extract data by name
>>> jpm_data = db.extract('JPM')
>>>
>>> # Create a new GlueDb
>>> new_db = api.newDb()
>>> new_db.post('prices', 'file:./prices.csv')
"""


def connect( uri ):
    """
    Connect to an existing GlueDb from a URI.

    Parameters
    ----------
    uri : str
        URI pointing to a ``.gluedb`` file or Python path to a GlueDb.

    Returns
    -------
    GlueDb
        The loaded GlueDb instance.

    Example
    -------
    >>> db = connect('pyswark:/data/sma-example.gluedb')
    >>> db = connect('python://mymodule.MY_GLUEDB')
    """
    from pyswark.gluedb import extractor
    return extractor.Contents( uri=uri ).extract()

def newDb():
    """
    Create a new empty GlueDb.

    Returns
    -------
    GlueDb
        An empty GlueDb instance ready for populating with records.

    Example
    -------
    >>> db = newDb()
    >>> db.post('prices', 'file:./prices.csv')
    >>> db.post('config', {'window': 60})
    """
    from pyswark.gluedb import db
    return db.GlueDb()

def newHub():
    """
    Create a new empty GlueHub.

    A GlueHub is a collection of GlueDb instances, useful for organizing
    multiple related databases.

    Returns
    -------
    GlueHub
        An empty GlueHub instance.

    Example
    -------
    >>> hub = newHub()
    >>> hub.post('market_data', market_db)
    >>> hub.post('config', config_db)
    """
    from pyswark.gluedb import hub
    return hub.GlueHub()