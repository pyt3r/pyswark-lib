from typing import Union

from pyswark.gluedb import recordmodel, loader, db


class Contents(recordmodel.Contents):
    gluedb : Union[str, db.GlueDb]

    def load(self):

        gluedb = loader.Contents(uriOrDb=self.gluedb).load()

        if isinstance( gluedb, GlueHub ):
            raise TypeError( f"Expected type=GlueDb, got type=GlueHub" )

        if not isinstance(gluedb, db.GlueDb):
            raise TypeError( f"Expected type=GlueDb, got type={ type(gluedb) }" )

        return gluedb


GlueDb = db.makeDb(Contents)


class GlueHub( GlueDb ):

    def post(self, name, body: Union[str, recordmodel.BodyType]):
        """ creates a new record in the db """
        if isinstance( body, str ):
            body = Contents( gluedb=body )

        return super().post(name, body)

    def toDb(self) -> db.GlueDb:
        """ consolidates to db """
        gluedb = db.GlueDb()
        for name in self.getNames():
            gluedb.merge( self.load( name ))
        return gluedb
