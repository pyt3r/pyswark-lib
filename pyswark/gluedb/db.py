"""
GlueDb Database Models
======================

This module defines the core GlueDb class and associated models for
managing data catalogs. A GlueDb stores named records that point to
data sources, enabling versioned and shareable data catalogs.
"""

from typing import Optional, Union
from pydantic import Field, create_model

from pyswark.core.io import contents
from pyswark.gluedb import dbmodel, recordmodel


class Extractor( contents.Contents ):
    """Extractor for reading data from URIs within GlueDb."""
    uri              : str
    datahandler      : Optional[ str ] = ""
    kw               : Optional[ dict ] = Field( default_factory=lambda: {} )


class Loader( contents.Contents ):
    """Loader for writing data to URIs within GlueDb."""
    uri              : str
    datahandler      : Optional[ str ] = ""
    kw               : Optional[ dict ] = Field( default_factory=lambda: {} )


class Contents( contents.Contents ):
    """
    Contents model for GlueDb records.

    Defines how data is extracted (read) and loaded (written) for a
    GlueDb record. Supports separate configurations for reading and
    writing operations.
    """

    # for extracting (reading)
    uri              : str
    datahandler      : Optional[ str ] = ""
    kw               : Optional[ dict ] = Field( default_factory=lambda: {} )

    # for loading (writing)
    datahandlerWrite : Optional[ str ] = ""
    kwWrite          : Optional[ dict ] = Field( default_factory=lambda: {} )

    @classmethod
    def fromArgs( cls, uri, datahandler="", kw=None, datahandlerWrite="", kwWrite=None ):
        """ create the model from args """
        return cls( uri=uri, datahandler=datahandler, kw=kw or {}, datahandlerWrite=datahandlerWrite, kwWrite=kwWrite or {} )

    def extract( self ):
        extractor = Extractor( uri=self.uri, datahandler=self.datahandler, kw=self.kw or {} )
        return extractor.read()

    def load( self, data ):
        """ the L in ETL - loads the contents into a system """
        datahandler = self.datahandlerWrite or self.datahandler
        loader = Loader( uri=self.uri, datahandler=datahandler, kw=self.kwWrite )
        return loader.write( data )


def _makeDb( ContentsModel, RecordModel, base ):
    """ makes a db class from a contents model """
    RecordModel = recordmodel.makeRecord( ContentsModel, RecordModel )

    Model = create_model(
        "GlueDb",
        __base__ = base,
        records  = ( Union[ str, list, list[ RecordModel ]], ... )
    )
    # ClassVars
    Model.Record   = RecordModel
    Model.Contents = ContentsModel

    return Model


_Record = recordmodel.makeRecord( Contents )
Record  = recordmodel.makeRecord( Contents, _Record )

_GlueDb = _makeDb( Contents, Record, dbmodel.Db )


class GlueDb( _GlueDb ):
    """
    A database of named data sources.

    GlueDb is the central abstraction for managing data catalogs in pyswark.
    It stores named records that point to data sources (URIs, Python objects,
    or inline data), enabling versioned and shareable data management.

    Methods
    -------
    post(name, uri_or_data)
        Add a new record to the database.
    extract(name)
        Load and return data by record name.
    getNames()
        List all record names in the database.
    merge(otherDb)
        Combine records from another GlueDb.

    Example
    -------
    >>> from pyswark.gluedb import api
    >>> db = api.newDb()
    >>> db.post('prices', 'file:./prices.csv')
    >>> db.post('config', 'file:./config.json')
    >>> print(db.getNames())
    ['prices', 'config']
    >>> prices_df = db.extract('prices')
    """

    def merge( self, otherDb ):
        """
        Merge records from another GlueDb into this one.

        Parameters
        ----------
        otherDb : GlueDb
            Another GlueDb instance to merge.

        Raises
        ------
        TypeError
            If otherDb is not a GlueDb instance.
        """
        if not isinstance( otherDb, GlueDb ):
            raise TypeError( f"can only add type=GlueDb, got type={ type(otherDb) }" )
        super().merge( otherDb )


def makeDb( ContentsModel, RecordModel=Record ):
    """
    Factory function to create custom GlueDb classes.

    Parameters
    ----------
    ContentsModel : type
        Custom Contents model for records.
    RecordModel : type, optional
        Custom Record model.

    Returns
    -------
    type
        A new GlueDb subclass with the specified models.
    """
    return _makeDb( ContentsModel, RecordModel, GlueDb  )
