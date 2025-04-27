from enum import Enum


class AliasEnum( Enum ):
    """ allows an entry to be aliased:

    class Example( AliasEnum ):
        X = 1, 'x'
        Y = 2
        Z = 3, [ 'z', 'zz', 'zzz' ]

    >> Example.Z.value
    >> Example.get('zz').value
    >> Example.get('z').value
    >> Example.get( Example.Z ).value
    """

    def __init__( self, value, aliases=() ):

        name = super().name

        if not isinstance( aliases, ( list, tuple )):
            aliases = ( aliases, )

        aliases = set([ name ] + list( aliases ))

        self._validateNewMember( aliases )
        self._aliases = aliases
        self._name  = name
        self._value = value

    @classmethod
    def _validateNewMember( cls, aliases ):
        dupes = {}
        for name, member in cls.__members__.items():
            dupe = member.aliases & aliases
            if dupe:
                dupes[ name ] = dupe
        if dupes:
            raise ValueError( f"duplicate alias for {dupes}")

    @property
    def aliases(self):
        return self._aliases

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @classmethod
    def get( cls, aliasOrMember ):
        """ gets the enum member by enum, attr, and finally alias """
        if isinstance( aliasOrMember, cls ):
            return aliasOrMember

        try:
            return super().__getattr__( aliasOrMember )

        except AttributeError:
            return cls._getByAlias( aliasOrMember )

    @classmethod
    def _getByAlias( cls, alias ):
        for name, member in cls.__members__.items():
            member = getattr( cls, name )
            if alias in member.aliases:
                return member
        raise ValueError( f'member not found for { alias= }' )
