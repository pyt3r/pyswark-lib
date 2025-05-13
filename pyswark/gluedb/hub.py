from typing import Union
from pyswark.gluedb import recordmodel, loader, db


class Contents( loader.Contents ):

    def load(self):
        loaded = super().load()

        if isinstance( loaded, GlueHub ):
            raise TypeError( f"Expected type=GlueDb, got type=GlueHub" )

        return loaded


GlueDb = db.makeDb( Contents )


class GlueHub( GlueDb ):

    def post(self, name, body: Union[str, recordmodel.BodyType]):
        """ creates a new record in the db """
        if isinstance( body, str ):
            body = Contents( uri=body )

        return super().post( name, body )

    def toDb(self) -> db.GlueDb:
        """ consolidates to db """
        gluedb = db.GlueDb()
        for name in self.getNames():
            gluedb.merge( self.load( name ))
        return gluedb
