from typing import ClassVar
from pydantic import field_validator

from pyswark.lib.pydantic import base

from pyswark.core.models import info, body, mixin


class Record( base.BaseModel, mixin.TypeCheck ):
    Info : ClassVar[ str ] = f"python:{ info.Info.getUri() }"
    Body : ClassVar[ str ] = f"python:{ body.Body.getUri() }"
    info : info.Info
    body : body.Body

    @field_validator( 'info', mode='after' )
    def _info_after( cls, info ):
        cls.checkIfInstance( info, cls.Info )
        return info

    @field_validator( 'body', mode='after' )
    def _body_after( cls, body ):
        cls.checkIfInstance( body, cls.Body )
        return body
