from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, ClassVar
from pydantic import field_validator
from pyswark.lib.pydantic import base

from pyswark.core.models.info import Info, InfoSQLModel
from pyswark.core.models.body import Body, BodySQLModel
from pyswark.core.models import mixin


class Record( base.BaseModel, mixin.TypeCheck ):
    InfoType : ClassVar[ str ] = "pyswark.core.models.info.Info"
    BodyType : ClassVar[ str ] = "pyswark.core.models.body.Body"
    info     : Info
    body     : Body

    @field_validator( 'info', mode='after' )
    def _info_after( cls, info ):
        cls.checkIfInstance( info, cls.InfoType )
        return info

    @field_validator( 'body', mode='after' )
    def _body_after( cls, body ):
        cls.checkIfInstance( body, cls.BodyType )
        return body

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
    info : Optional[InfoSQLModel] = Relationship( back_populates="record" )
    body : Optional[BodySQLModel] = Relationship( back_populates="record" )

    def asModel( self ):
        return Record( 
            info = self.info.asModel(), 
            body = self.body.asModel(),
        )