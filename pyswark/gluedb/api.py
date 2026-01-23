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
>>> from pyswark.gluedb import db
>>> new_db = db.Db()
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
    Db
        The loaded GlueDb instance (pyswark.gluedb.db.Db).

    Example
    -------
    >>> db = connect('pyswark:/data/sma-example.gluedb')
    >>> db = connect('python://mymodule.MY_GLUEDB')
    """
    from pyswark.core.io import api
    return api.read( uri )
