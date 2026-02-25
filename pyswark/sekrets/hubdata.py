from pyswark.sekrets import hub
from pyswark.sekrets.settings import Settings


DBs = [
    Settings.SGDRIVE2,
    Settings.PRIVATE_CONDA,
    Settings.REDIS,
    Settings.EXAMPLE_IAC,
    Settings.GDRIVE2,
]

HUB = hub.Hub()
_ = [ HUB.post( setting.uri, name=setting.name ) for setting in DBs ]
