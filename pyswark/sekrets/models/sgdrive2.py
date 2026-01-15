from pyswark.gluedb import db
from pyswark.lib.pydantic import base
from pyswark.core.models import extractor

class Contents( base.BaseModel ):
    client_id     : str
    client_secret : str
    profile       : str
    path          : str

    def extract( self ):
        return self.model_dump()


Db = db.makeDb( Contents )
