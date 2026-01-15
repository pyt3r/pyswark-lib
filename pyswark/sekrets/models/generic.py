from typing import Optional, Any
from pyswark.lib.pydantic import base
from pyswark.gluedb import db

class Contents( base.BaseModel ):
    sekret      : Any
    description : Optional[ str ] = ""

    def extract( self ):
        return self.model_dump()


Db = db.makeDb( Contents )
