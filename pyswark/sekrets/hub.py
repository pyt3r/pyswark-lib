from pyswark.gluedb import hub
from pyswark.sekrets.settings import Settings

DBs = [
    Settings.SGDRIVE2,
    Settings.PRIVATE_CONDA,
    Settings.REDIS,
    Settings.EXAMPLE_IAC,
]
 
HUB = hub.GlueHub()
_ = [ HUB.post( setting.uri, name=setting.name ) for setting in DBs ]
