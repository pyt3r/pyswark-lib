from pyswark.gluedb import api
from pyswark.sekrets.settings import Settings

DBs = {
    Settings.SGDRIVE2      : "python://pyswark.sekrets.db.SGDRIVE2",
    # Settings.PRIVATE_CONDA : "python://pyswark.sekrets.db",
    # Settings.REDIS         : "python://pyswark.sekrets.db",
    Settings.EXAMPLE_IAC   : "python://pyswark.sekrets.db.EXAMPLE_IAC",
}
 
HUB = api.newHub()
_ = [ HUB.post( const.name, gluedb ) for const, gluedb in DBs.items() ]
