import aenum


class Alias:
    """ Holds a set of aliases
    >>  Alias( 'a', 'b' ).valueset # --> {'a', 'b'}
    >>  Alias(['a', 'b']).valueset # --> {'a', 'b'}
    >>  Alias(('a', 'b')).valueset # --> {'a', 'b'}
    >>  Alias({'a', 'b'}).valueset # --> {'a', 'b'}
    """
    def __init__( self, alias, *aliases ):

        if not isinstance( alias, ( set, list, tuple )):
            alias = [ alias ]

        self._valueset = set( list( alias ) + list( aliases ) )

    @property
    def valueset(self):
        return self._valueset

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{ self.__class__.__name__}({ self.valueset })"



class AliasEnum( aenum.Enum ):
    """ allows an entry to be aliased:

    class Example( AliasEnum ):
        X = 1, Alias('x')
        Y = 2
        Z = 3, Alias('z', 'zz', 'zzz')

    >> Example.Z.value
    >> Example.get('zz').value
    >> Example.get('z').value
    >> Example.get( Example.Z ).value
    """

    _settings_ = aenum.NoAlias

    def __init__( self, *values ):

        alias = Alias(())

        if len( values ) == 1:
            values = values[0]

        elif len( values ) == 2 and isinstance( values[-1], Alias ):
            values, alias = values

        elif len( values ) > 2 and isinstance( values[-1], Alias ):
            *values, alias = values

        else:
            values = tuple( values )

        name    = super().name
        aliases = { name } | alias.valueset

        self._validateNewMember( aliases )
        self._aliases = aliases
        self._name  = name
        self._value = values

    def __repr__(self):
        return f"name={ self.name }, value={ self.value }, aliases={ sorted( self.aliases )}"

    @classmethod
    def _validateNewMember( cls, aliases ):
        dupes = {}
        for name, member in cls.__members__.items():
            dupe = member.aliases & aliases
            if dupe:
                dupes[ name ] = dupe
        if dupes:
            raise AliasEnumError( f"duplicate alias for {dupes}")

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
        raise AliasEnumError( f'member not found for {alias=}' )

    @classmethod
    def toMapping( cls, attr='value' ):
        mapping = {}
        for name, member in cls.__members__.items():
            member = getattr( cls, name )
            value  = getattr( member, attr )
            for key in [ name ] + sorted(member.aliases):
                mapping[ key ] = value
        return mapping

    @classmethod
    def tryGet( cls, aliasOrMember, default=None ):
        try:
            return cls.get( aliasOrMember )
        except AliasEnumError:
            return default



class AliasEnumError( Exception ):
    pass