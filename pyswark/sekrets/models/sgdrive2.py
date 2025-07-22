from pyswark.gluedb import db
from pyswark.core.models import extractor

class Contents( extractor.Extractor ):
    client_id     : str
    client_secret : str
    profile       : str
    path          : str

    def extract( self ):
        return self.model_dump()


Db = db.makeDb( Contents )
