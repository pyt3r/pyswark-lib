def load( uriOrDb ):
    from pyswark.core.gluedb import loader
    return loader.Loader( uriOrDb=uriOrDb ).load()

def new():
    from pyswark.core.gluedb import db
    return db.GlueDb()