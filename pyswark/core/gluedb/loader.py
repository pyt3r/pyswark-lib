from typing import Union

from pyswark.core.io import api
from pyswark.core.gluedb import dbmodel, recordmodel


class Contents( recordmodel.Contents ):
    uriOrDb: Union[str, dbmodel.Db]

    def load(self) -> dbmodel.Db:
        uriOrDb = self.uriOrDb

        if isinstance( uriOrDb, str ):
            uriOrDb = api.read( uriOrDb )

        if not isinstance(uriOrDb, dbmodel.Db):
            raise TypeError( f"Expected type=interface.Db, got type={ type(uriOrDb) }" )

        return uriOrDb



