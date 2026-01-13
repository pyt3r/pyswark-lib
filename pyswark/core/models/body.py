import json

from typing import ClassVar, Union
from pydantic import field_validator, model_validator
from pyswark.lib.pydantic import base

from pyswark.core.models import mixin


class Body( base.BaseModel, mixin.TypeCheck ):
    """Base class for record body."""
    Base     : ClassVar[ str ] = f"python:{ base.BaseModel.getUri() }"
    Allow    : ClassVar[ Union[ tuple, list, str, None ]] = None
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
        cls.checkIfAllowedType( model, cls.Allow )
        return model

    def extract( self ):
        return self.fromDict({
            'model'    : self.model,
            'contents' : json.loads( self.contents ),
        })
