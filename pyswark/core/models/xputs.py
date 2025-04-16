from pyswark.lib.pydantic.base import BaseModel


class _BaseXputs( BaseModel ):

    def __init__(self, *args, **kwargs ):
        anames  = list( self.__annotations__.keys() )
        akwargs = dict( zip( anames, args ))
        return super().__init__( **akwargs, **kwargs )


class BaseInputs( _BaseXputs ):
    """ base inputs """


class BaseOutputs( _BaseXputs ):
    """ base outputs """