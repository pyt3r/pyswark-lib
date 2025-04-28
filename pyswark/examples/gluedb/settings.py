from pyswark.lib import aenum
from pyswark.examples import gluedb


class Settings(aenum.AliasEnum):
    _ROOT    = gluedb.__name__
    HUB     = f'{ _ROOT }.hub'
    DB      = f'{ _ROOT }.db'
    RECORDS = f'{ _ROOT }.records'
    OBJECTS = f'{ _ROOT }.objects'

    @property
    def uri(self):
        return f"python://{ self.value }"