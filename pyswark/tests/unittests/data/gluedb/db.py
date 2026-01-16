from pyswark.core.io import api
from pyswark.gluedb import db
from pyswark.tests.unittests.data.gluedb.settings import Settings


_RECORDS_1 = api.read(f'{ Settings.RECORDS.uri }.RECORDS_1')
_RECORDS_2 = api.read(f'{ Settings.RECORDS.uri }.RECORDS_2')


DB_1 = db.Db( records=_RECORDS_1 )
DB_2 = db.Db( records=_RECORDS_2 )
