from typing import Union

from pyswark.core.gluedb import interface
from pyswark.core.gluedb import db, loader


class Contents( interface.Contents ):
    gluedb : Union[ str, db.GlueDb ]

    def load(self):
        gluedb = self.gluedb

        if isinstance( gluedb, str ):
            gluedb = loader.Loader( uriOrDb=gluedb ).load()

        if isinstance( gluedb, GlueHub ):
            raise TypeError( f"Expected type=GlueDb, got type=GlueHub" )

        if not isinstance( gluedb, db.GlueDb ):
            raise TypeError( f"Expected type=GlueDb, got type={ type(gluedb) }" )

        return gluedb


GlueDb = db.makeDb( Contents )


class GlueHub( GlueDb ):
    def create(self, name, contents: Union[ str, dict, Contents ]):
        """ creates a new record in the db """
        if isinstance( contents, str ):
            contents = { 'gluedb': contents }

        return super().create( name, contents )

    def toDb(self) -> db.GlueDb:
        """ consolidates to db """
        gluedb = db.GlueDb()
        for name in self.getNames():
            gluedb.merge( self.load( name ))
        return gluedb
