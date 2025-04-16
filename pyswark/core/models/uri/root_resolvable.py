from typing import ClassVar
from pydantic import AnyUrl, field_validator
from pyswark.core.models.uri.root import UriRootModel


class Resolvable( UriRootModel ):
    root        : str
    EXT_HANDLER : ClassVar[ str ] = ""

    _STARTSWITH    : ClassVar = []
    _ENDSWITH      : ClassVar = []
    _NOTSTARTSWITH : ClassVar = []
    _CONTAINS      : ClassVar = []

    @field_validator( 'root', mode='after' )
    @classmethod
    def resolve( cls, root: str ) -> AnyUrl:
        assert ':' not in root, f"root='{ root }' already has a protocol"
        cls._assertions( root )
        return cls._resolve( root )

    @classmethod
    def _assertions( cls, root ):

        cond  = True if cls._STARTSWITH or cls._ENDSWITH or cls._NOTSTARTSWITH or cls._CONTAINS else None
        valid = False if cond else True

        if cls._STARTSWITH:
            startswith = tuple( f'{s}' for s in cls._STARTSWITH )
            valid = valid or root.startswith( startswith )

        if cls._ENDSWITH:
            endswith = tuple( f'{e}' for e in cls._ENDSWITH )
            valid = valid or root.endswith( endswith )

        if cls._NOTSTARTSWITH:
            notstartswith =  tuple( f'{s}' for s in cls._NOTSTARTSWITH )
            valid = valid or not root.startswith( notstartswith )

        if cls._CONTAINS:
            valid = valid or any( c in root for c in cls._CONTAINS )

        assert valid, f"Does not look like a {cls.__name__} uri"

    @staticmethod
    def _resolve( root ):
        raise NotImplementedError