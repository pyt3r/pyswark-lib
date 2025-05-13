from pydantic import model_validator, Field
from pyswark.core.io import api
from pyswark.gluedb import recordmodel, dbmodel


class Contents( recordmodel.Contents ):
    uri : str
    kw  : dict = Field( default_factory=lambda: {} )

    @model_validator( mode='after' )
    def _validate(self):
        if self.uri.startswith( "python:" ):
            self.kw = { "reloadmodule": True }
        return self

    def load(self) -> dbmodel.Db:
        loaded = api.read( self.uri, **self.kw )

        if not isinstance( loaded, dbmodel.Db ):
            raise TypeError( f"Expected type=interface.Db, got type={ type(loaded) }" )

        return loaded
