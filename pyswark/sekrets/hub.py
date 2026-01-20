from pyswark.gluedb import api
from pyswark.sekrets.settings import Settings

DBs = {
    Settings.SGDRIVE2      : "python://pyswark.sekrets.db.SGDRIVE2",
    Settings.PRIVATE_CONDA : "python://pyswark.sekrets.db.PRIVATE_CONDA",
    Settings.REDIS         : "python://pyswark.sekrets.db.REDIS",
    Settings.EXAMPLE_IAC   : "python://pyswark.sekrets.db.EXAMPLE_IAC",
}
 
HUB = api.newHub()
_ = [ HUB.post( uri, name=const.name ) for const, uri in DBs.items() ]
