from typing import Optional, Union
from datetime import datetime
import sqlmodel
from sqlmodel import SQLModel, Relationship
import pydantic
from pydantic import field_validator
from pyswark.lib.pydantic import base
from pyswark.core.models.datetime import Datetime


class Info( base.BaseModel ):
    """Base class for record metadata/info."""
    name          : str
    date_created  : Union[ Datetime, str, dict, None ] = pydantic.Field( default='', validate_default=True )
    date_modified : Union[ Datetime, str, dict, None ] = pydantic.Field( default='', validate_default=True )

    def clone( self, **kwargs ):
        """ set multiple attributes and return a new Info object """
        dump = self.model_dump()
        for k, v in kwargs.items():
            if k in dump:
                dump[k] = v
        return Info( **dump )

    @field_validator( 'date_created', 'date_modified', mode='before' )
    def _date( cls, date ):
        if not date:
            date = Datetime.now( 'UTC' )
        if isinstance( date, dict ):
            date = Datetime( **date )
        elif not isinstance( date, Datetime ):
            date = Datetime( date )
        return date

    def asSQLModel( self ):
        """Convert to SQLModel, extracting Python datetime from Datetime instances."""
        return InfoSQLModel( 
            name          = self.name,
            date_created  = self.date_created.datetime,
            date_modified = self.date_modified.datetime,
        )


class InfoSQLModel( SQLModel, table=True ):
    """
    Record metadata - SQLModel version of pyswark.core.models.info.Info
    
    Stores identifying information about a record.
    """

    id            : Optional[int] = sqlmodel.Field( default=None, primary_key=True )
    name          : str           = sqlmodel.Field( index=True, unique=True )  # Indexed for fast lookups
    date_created  : datetime      = sqlmodel.Field( default=None, index=True )
    date_modified : datetime      = sqlmodel.Field( default=None, index=True )

    # Relationship back to Record (fully qualified path for cross-module resolution)
    record : Optional["pyswark.core.models.record.RecordSQLModel"] = Relationship( back_populates="info" )

    def asModel( self ):
        return Info( 
            name          = self.name,
            date_created  = self.date_created,
            date_modified = self.date_modified,
        )
