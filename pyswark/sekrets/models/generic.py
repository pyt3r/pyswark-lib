from typing import Optional, Any
from pyswark.core.models import extractor
from pyswark.gluedb import db

class Contents( extractor.Extractor ):
    sekret      : Any
    description : Optional[ str ] = ""

    def extract( self ):
        return self.model_dump()


Db = db.makeDb( Contents )
