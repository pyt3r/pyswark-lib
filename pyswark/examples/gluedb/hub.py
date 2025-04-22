from pyswark.core.gluedb import hub
from pyswark.examples.gluedb.settings import Settings

DBs = {
    'db_1' : f'{ Settings.DB.uri }.DB_1',
    'db_2' : f'{ Settings.DB.uri }.DB_2',
}

HUB = hub.GlueHub()
_ = [ HUB.create( name, contents ) for name, contents in DBs.items() ]
