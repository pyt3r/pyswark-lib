from typing import Optional, Any
from pyswark.sekrets.models import base


class Sekret( base.Sekret ):
    sekret      : Any
    description : Optional[ str ] = ""
