from typing import Optional, ClassVar
from sqlmodel import SQLModel, Field, Relationship
from pyswark.lib.pydantic import base


class Info( base.BaseModel ):
    """Base class for record metadata/info."""
    name : str

    def asSQLModel( self ):
        return InfoSQLModel( name=self.name )


class InfoSQLModel( SQLModel, table=True ):
    """
    Record metadata - SQLModel version of pyswark.core.models.info.Info
    
    Stores identifying information about a record.
    """

    id     : Optional[int] = Field( default=None, primary_key=True )
    name   : str = Field( index=True, unique=True )  # Indexed for fast lookups

    # Relationship back to Record (fully qualified path for cross-module resolution)
    record : Optional["pyswark.core.models.record.RecordSQLModel"] = Relationship( back_populates="info" )

    def asModel( self ):
        return Info( name=self.name )