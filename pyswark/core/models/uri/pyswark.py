import pathlib
from typing import ClassVar
from pydantic import Field

import pyswark
from pyswark.core.models.uri import interface


class Inputs( interface.InputsWithUriPatch ):
    uri    : str
    SCHEME : ClassVar = 'pyswark'


class Model( interface.Model ):
    inputs  : Inputs
    outputs : interface.Outputs = Field( default=None, description="" )
    SCHEME  : ClassVar = Inputs.SCHEME

    @property
    def Path(self):
        parent = pathlib.Path( pyswark.__file__ ).parent
        return pathlib.Path( f'{ parent }/{ super().Path }' )



