
from typing import ClassVar
from pydantic import Field, ValidationError

from pyswark.core.models.uri import interface, generic, file, http


class Inputs( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = ''


class Model( interface.Model ):
    inputs  : Inputs
    outputs : interface.Outputs = Field( default=None, description="" )

    def __new__( cls, uri ):
        try:
            model = generic.Model( uri )
            if model.host:
                model = http.ModelGuess( uri )
            return model

        except ValidationError:
            return file.ModelGuess( f'file:{ uri }' )
