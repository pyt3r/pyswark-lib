import json
from typing import ClassVar, Union, Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator, model_validator
from pyswark.lib.pydantic import base

from pyswark.core.models import mixin


class Body( base.BaseModel, mixin.TypeCheck ):
    """Base class for record body."""
    Base     : ClassVar[ Union[ str, type ] ] = base.BaseModel.getUri()
    model    : str
    contents : str

    @model_validator( mode='before' )
    @classmethod
    def _before( cls, kw ):
        """Handle both dict input and BaseModel instance input."""
        model    = kw.get( 'model' )
        contents = kw.get( 'contents' )

        if not isinstance( model, str ) and cls.isInstance( model, cls.Base ):
            kw = model.toDict()
            model    = kw.get( 'model' )
            contents = kw.get( 'contents' )

        return { 
            'model'    : model,
            'contents' : contents if isinstance( contents, str ) else json.dumps( contents ),
        }

    @field_validator( 'model', mode='after' )
    def _model_after( cls, model ):
        cls.checkIfSubclass( model, cls.Base )
        return model

    def extract( self ):
        return self.fromDict({
            'model'    : self.model,
            'contents' : json.loads( self.contents ),
        })

    def asSQLModel( self ):
        return BodySQLModel( 
            model    = self.model, 
            contents = self.contents,
        )


class BodySQLModel( SQLModel, table=True ):
    """
    Record body - SQLModel version of pyswark.core.models.body.Body
    
    Stores the model class path and serialized contents.
    This enables storing arbitrary Pydantic models as JSON strings.
    
    Note: SQLModel table validators don't run reliably during ORM operations.
    Use the `create()` classmethod for auto-serialization of dict contents.
    """
    id       : Optional[int] = Field( default=None, primary_key=True )
    model    : str  # Class path, e.g., "myapp.models.MyModel"
    contents : str  # JSON-serialized model data (must be a string!)
    
    # Relationship back to Record (fully qualified path for cross-module resolution)
    record : Optional["pyswark.core.models.record.RecordSQLModel"] = Relationship( back_populates="body" )
    
    def asModel( self ):
        return Body( 
            model    = self.model, 
            contents = self.contents,
        )
