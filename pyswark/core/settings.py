from enum import Enum


class Settings( Enum ):
    """ allows an entry to be aliased:

    class Example( Settings ):
        X = ('x', 1)
        Y = 2

    >> Example.X.name == 'x'
    >> Example.X.value == 1

    >> Example.Y.name == 'Y'
    >> Example.Y.value == 2

    """

    def __init__(self, name, *others):
        if not others:
            self._name = super().name
            self._value = name
        else:
            value, *others = others
            self._name = name
            self._value = value

        self._others = others

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def string(self):
        return str( self.value )

    @classmethod
    def getMember( cls, aliasOrMember ):
        if isinstance( aliasOrMember, cls ):
            return aliasOrMember
        return cls._getByName( aliasOrMember )

    @classmethod
    def _getByName( cls, alias ):
        """ Gets the enum from the member or member string:
          >> Example.getEnum( 'X' ).name -> 'x'
        """
        members = []
        for k in cls.__members__.keys():
            member = getattr( cls, k )
            if member.name == alias:
                members.append( member )

        if len( members ) == 0:
            raise ValueError(f"{ cls } has no members with alias='{ alias }'")

        if len( members ) > 1:
            raise ValueError(f"{ cls } has more than one members with alias='{ alias }'")

        else:
            return members.pop()
