from pyswark.lib.pydantic import base


class Loader( base.BaseModel ):

    def load( self ):
        raise NotImplementedError
