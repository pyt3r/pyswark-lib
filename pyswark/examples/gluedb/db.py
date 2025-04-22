from pyswark.core.gluedb import db
from pyswark.examples.gluedb.settings import Settings


DB_1 = db.GlueDb( f'{ Settings.RECORDS.uri }.RECORDS_1' )
DB_2 = db.GlueDb( f'{ Settings.RECORDS.uri }.RECORDS_2' )
