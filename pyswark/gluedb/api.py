def load( uri ):
    from pyswark.gluedb import loader
    return loader.Contents( uri=uri ).load()

def newDb():
    from pyswark.gluedb import db
    return db.GlueDb()

def newHub():
    from pyswark.gluedb import hub
    return hub.GlueHub()