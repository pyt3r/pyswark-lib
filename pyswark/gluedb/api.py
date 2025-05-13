def load( uri ):
    from pyswark.gluedb import loader
    return loader.Contents( uri=uri ).load()

def new():
    from pyswark.gluedb import db
    return db.GlueDb()