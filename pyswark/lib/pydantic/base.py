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

    @staticmethod
    def fromJson( *a, **kw ):
        from pyswark.lib.pydantic import ser_des
        return ser_des.fromJson( *a, **kw )

    def toDict( self ):
        from pyswark.lib.pydantic import ser_des
        return ser_des.toDict( self )

    @staticmethod
    def fromDict( *a, **kw ):
        from pyswark.lib.pydantic import ser_des
        return ser_des.fromDict( *a, **kw )

    @classmethod
    def getUri(cls):
        return f"{ cls.__module__}.{ cls.__name__}"
