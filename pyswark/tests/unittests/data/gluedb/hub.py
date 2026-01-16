from pyswark.gluedb import hub
from pyswark.tests.unittests.data.gluedb.settings import Settings

DBs = {
    'db_1' : f'{ Settings.DB.uri }.DB_1',
    'db_2' : f'{ Settings.DB.uri }.DB_2',
}

HUB = hub.GlueHub()
_ = [ HUB.post( gluedb, name=name ) for name, gluedb in DBs.items() ]

print()
