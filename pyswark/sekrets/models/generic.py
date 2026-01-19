from typing import Optional, Any
from pyswark.sekrets import base


class Sekret( base.Sekret ):
    sekret      : Any
    description : Optional[ str ] = ""
