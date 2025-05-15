from typing import Union
from pyswark.gluedb import recordmodel, loader, db


class Contents( loader.Contents ):

    def load(self):
        loaded = super().load()

        if isinstance( loaded, GlueHub ):
            raise TypeError( f"Expected type=GlueDb, got type=GlueHub" )

        return loaded


_Record = recordmodel.makeRecord( Contents )

class Record( _Record ):

    @classmethod
    def validate( cls, body ):
        expected = cls.Contents.getUri()
        model    = body['model']
        if model != expected:
            raise ValueError( f"contents has invalid uri: expected model='{expected}', got {model=}" )

GlueDb = db.makeDb( Contents, Record )


class GlueHub( GlueDb ):

    def post(self, name, body: Union[str, recordmodel.Body]):
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

    def merge(self, otherHub):
        """ merge the contents of another hub """
        if not isinstance(otherHub, GlueHub):
            raise TypeError( f"can only add type GlueHub, got type={ type(otherDb) }" )
        super().merge( otherHub )

