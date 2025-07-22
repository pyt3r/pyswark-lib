from functools import lru_cache
from pyswark.gluedb import api
from pyswark.sekrets.settings import Settings


def get( username, protocol ):
    """ get sekret for a username and protocol """
    db = getDb( _getProtocolName( protocol ))
    return db.extract( username )

@lru_cache()
def getDb( protocol ):
    hub = getHub()
    return hub.extract(_getProtocolName(protocol))

@lru_cache()
def getHub():
    from pyswark.sekrets import hub

    return api.connect( f"python://{ hub.__name__}.HUB" )

@lru_cache()
def _getProtocolName( protocol ):
    return Settings.get( protocol ).name

