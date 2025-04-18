from pydantic import Field

from pyswark.core.models.uri import interface


class Model( interface.Model ):
    inputs  : interface.Inputs
    outputs : interface.Outputs = Field( default=None, description="" )

