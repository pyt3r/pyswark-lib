import pyswark.core.models.xputs
from pydantic import Field, field_validator, model_validator

from pyswark.lib.pydantic import base


class FunctionModel( base.BaseModel ):
    inputs  : pyswark.core.models.xputs.BaseInputs
    outputs : pyswark.core.models.xputs.BaseOutputs = Field(default=None, description="")

    def __init__(self, inputs=None, **kw ):
        """ keep **kw for outputs deserialization """
        super().__init__( inputs=inputs, **kw )

    @classmethod
    def validate(cls, inputs: pyswark.core.models.xputs.BaseInputs):
        return inputs

    @staticmethod
    def function(inputs):
        raise NotImplementedError

    @field_validator( "inputs", mode="before" )
    def _validate(cls, inputs):
        inputs = cls._coerceInputs( inputs )
        return cls.validate( inputs )

    @model_validator(mode="after")
    def _function(self):
        if self.outputs is None:
            outputs = self.function( self.inputs )
            self.outputs = self._coerceOutputs( outputs )
        return self

    @classmethod
    def _coerceInputs( cls, data ):
        return cls._coerce( data, 'inputs' )

    @classmethod
    def _coerceOutputs( cls, data ):
        return cls._coerce( data, 'outputs' )

    @classmethod
    def _coerce( cls, xputs, annotation ):
        klass = cls.__annotations__[ annotation ]

        if not issubclass( klass, base.BaseModel ):
            raise TypeError( f"xputs={klass} must be of subtype=BaseModel" )

        if isinstance( xputs, klass ):
            return xputs

        if isinstance( xputs, dict ):
            return klass( **xputs )

        return klass( xputs )
