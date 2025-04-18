
from typing import ClassVar
from pydantic import Field, ValidationError

from pyswark.core.models.uri import interface, generic, file


class Inputs( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = ''


class Model( interface.Model ):
    inputs  : Inputs
    outputs : interface.Outputs = Field( default=None, description="" )

    def __new__( cls, uri ):
        try:
            return generic.Model( uri )
        except ValidationError:
            return file.Model( f'file:{ uri }' )
