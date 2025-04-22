from typing import Union

from pyswark.core.io import api
from pyswark.core.gluedb import interface


class Loader( interface.Loader ):
    uriOrDb: Union[ str, interface.Db ]

    def load(self) -> interface.Db:
        uriOrDb = self.uriOrDb

        if isinstance( uriOrDb, str ):
            uriOrDb = api.read( uriOrDb )

        if not isinstance( uriOrDb, interface.Db ):
            raise TypeError( f"Expected type=interface.Db, got type={ type(uriOrDb) }" )

        return uriOrDb



