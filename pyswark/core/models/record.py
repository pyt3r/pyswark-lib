from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from pyswark.lib.pydantic import base

from pyswark.core.models.info import Info, InfoSQLModel
from pyswark.core.models.body import Body, BodySQLModel


class Record( base.BaseModel ):
    info     : Info
    body     : Body

    @field_validator( 'info', mode='before' )
    def _info_before( cls, info ):
        if isinstance( info, dict ):
            info = Info(**info)
        return info

    def acquire( self ):
        return self.body.extract()

    def asSQLModel( self ):
        return RecordSQLModel( 
            info = self.info.asSQLModel(), 
            body = self.body.asSQLModel(),
        )


class RecordSQLModel( SQLModel, table=True ):
    """
    Main record - SQLModel version of pyswark.core.models.record.Record
    
    Combines Info (metadata) and Body (content) with database relationships.
    """
    
    id      : Optional[int] = Field( default=None, primary_key=True )
    info_id : Optional[int] = Field( default=None, foreign_key="infosqlmodel.id" )
    body_id : Optional[int] = Field( default=None, foreign_key="bodysqlmodel.id" )
    
    # Relationships (module aliases avoid shadowing)
    info : InfoSQLModel = Relationship( back_populates="record" )
    body : BodySQLModel = Relationship( back_populates="record" )

    def asModel( self ):
        return Record( 
            info = self.info.asModel(), 
            body = self.body.asModel(),
        )
