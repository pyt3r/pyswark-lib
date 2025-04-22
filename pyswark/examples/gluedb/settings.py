from pyswark.core import settings
from pyswark.examples import gluedb


class Settings( settings.Settings ):
    _ROOT    = gluedb.__name__
    HUB     = f'{ _ROOT }.hub'
    DB      = f'{ _ROOT }.db'
    RECORDS = f'{ _ROOT }.records'
    OBJECTS = f'{ _ROOT }.objects'

    @property
    def uri(self):
        return f"python://{ self.value }"