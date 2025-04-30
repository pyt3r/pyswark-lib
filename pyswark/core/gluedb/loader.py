from typing import Union

from pyswark.core.io import api
from pyswark.core.models import contentsmodel
from pyswark.core.gluedb import interface


class Loader(contentsmodel.Loader):
    uriOrDb: Union[ str, interface.Db ]

    def load(self) -> interface.Db:
        uriOrDb = self.uriOrDb

        if isinstance( uriOrDb, str ):
            uriOrDb = api.read( uriOrDb )

        if not isinstance( uriOrDb, interface.Db ):
            raise TypeError( f"Expected type=interface.Db, got type={ type(uriOrDb) }" )

        return uriOrDb



