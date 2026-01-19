from pyswark.core.models import extractor


class Sekret( extractor.Extractor ):

    def extract( self ):
        return self.model_dump()
    