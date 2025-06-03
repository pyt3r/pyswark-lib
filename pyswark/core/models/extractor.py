from pyswark.lib.pydantic import base


class Extractor( base.BaseModel ):

    def extract( self ):
        raise NotImplementedError
