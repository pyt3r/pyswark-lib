from pyswark.sekrets.models import generic, sgdrive2
from pyswark.sekrets.settings import Settings

SGDRIVE2      = sgdrive2.Db( Settings.SGDRIVE2.uri )
PRIVATE_CONDA = generic.Db(  Settings.PRIVATE_CONDA.uri )
REDIS         = generic.Db(  Settings.REDIS.uri )
EXAMPLE_IAC   = generic.Db(  Settings.EXAMPLE_IAC.uri )
