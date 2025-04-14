from pydantic import BaseModel, ConfigDict


class ExtraForbidden( BaseModel ):
    model_config = ConfigDict( extra='forbid' )


class ExtraAllowed( BaseModel ):
    model_config = ConfigDict( extra='allow' )


class BaseModel( ExtraForbidden ):
    """ patched base model """

    def write( self, uri, overwrite=False, indent=2, **kw ):
        raise NotImplementedError

    def toJson( self, indent=2, **kw ):
        from pyswark.lib.pydantic import ser_des
        return ser_des.toJson( self, indent=indent, **kw )


class _BaseXputs( BaseModel ):

    def __init__(self, *args, **kwargs ):
        anames  = list( self.__annotations__.keys() )
        akwargs = dict( zip( anames, args ))
        return super().__init__( **akwargs, **kwargs )

class BaseInputs( _BaseXputs ):
    """ base inputs """

class BaseOutputs( _BaseXputs ):
    """ base outputs """
