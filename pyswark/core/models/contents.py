from pyswark.lib.pydantic import base


class Contents( base.BaseModel ):

    @classmethod
    def getUri(cls):
        return f"{ cls.__module__}.{ cls.__name__}"
