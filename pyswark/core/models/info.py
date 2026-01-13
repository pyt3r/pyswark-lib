from pyswark.lib.pydantic import base


class Info( base.BaseModel ):
    """Base class for record metadata/info."""
    name          : str
    # author      : None
