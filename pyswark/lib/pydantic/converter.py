from typing import Any
from pydantic import model_validator, field_validator

from pyswark.lib.pydantic import base


class ConverterModel( base.BaseModel ):
    """ for when you want to convert to an output that pydantic/typing doesnt natively support, i.e. an np.array """
    inputs: base.BaseInputs

    def __init__( self, inputs=None ):
        super().__init__( inputs=inputs )

    @classmethod
    def validate( cls, inputs: base.BaseInputs ):
        return inputs

    @classmethod
    def convert( cls, inputs: base.BaseInputs ) -> Any:
        return inputs

    @field_validator( 'inputs', mode='before' )
    def _validate( cls, inputs ):
        inputs = cls._coerceInputs( inputs )
        return cls.validate( inputs )

    @classmethod
    def _coerceInputs( cls, data ):
        return cls._coerce( data, 'inputs' )

    @classmethod
    def _coerce( cls, xputs, annotation ):
        klass = cls.__annotations__[ annotation ]

        if not issubclass( klass, base.BaseModel ):
            raise TypeError( f"xputs={klass} must be of subtype=BaseModel" )

        if isinstance( xputs, klass ):
            return xputs

        if isinstance( xputs, dict ):
            if len(xputs) == 1 and annotation in xputs:
                return klass( **xputs[ annotation ])
            return klass( **xputs )

        return klass( xputs )

    @model_validator( mode='after' )
    def _convert( self ) -> Any:
        self._outputs = self.convert( self.inputs )
        return self

    @property
    def outputs(self):
        return self._outputs

