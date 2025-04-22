from typing import Union
from pyswark.lib.pydantic import base


class Loader( base.BaseModel ):

    def load( self ):
        return self


class Contents( Loader ):

    @classmethod
    def getUri(cls):
        return f"python://{ cls.__module__}.{ cls.__name__}"


class Record( base.BaseModel ):
    name     : str
    model    : str
    contents : Union[ Contents, dict ]
