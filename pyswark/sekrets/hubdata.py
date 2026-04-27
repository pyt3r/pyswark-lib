from pyswark.sekrets import hub
from pyswark.sekrets.settings import Settings


DBs = [
    Settings.GDRIVE2,
]

HUB = hub.Hub()
_ = [ HUB.post( setting.uri, name=setting.name ) for setting in DBs ]
