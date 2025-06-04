def connect( uri ):
    from pyswark.gluedb import extractor
    return extractor.Contents( uri=uri ).extract()

def newDb():
    from pyswark.gluedb import db
    return db.GlueDb()

def newHub():
    from pyswark.gluedb import hub
    return hub.GlueHub()