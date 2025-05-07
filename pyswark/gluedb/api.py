def load( uriOrDb ):
    from pyswark.gluedb import loader
    return loader.Contents(uriOrDb=uriOrDb).load()

def new():
    from pyswark.gluedb import db
    return db.GlueDb()