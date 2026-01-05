"""
Advanced Enum with Aliases
==========================

This module provides an enhanced enum class that supports aliases,
allowing multiple names to refer to the same enum member.

Classes
-------
AliasEnum
    Enum class supporting aliases for members.
Alias
    Helper class to define aliases for enum members.

Example
-------
>>> from pyswark.lib.aenum import AliasEnum, Alias
>>>
>>> class Protocol(AliasEnum):
...     HTTP = 80, Alias('http', 'web')
...     HTTPS = 443, Alias('https', 'secure')
...     SSH = 22
>>>
>>> Protocol.get('http')  # Returns Protocol.HTTP
>>> Protocol.get('secure')  # Returns Protocol.HTTPS
"""

import aenum
from pyswark.lib.enum import Mixin


class Alias:
    """
    Container for alias values.

    Holds a set of aliases that can be used with AliasEnum to allow
    multiple names to reference the same enum member.

    Parameters
    ----------
    alias : str or list or tuple or set
        Primary alias or collection of aliases.
    *aliases : str
        Additional aliases.

    Attributes
    ----------
    valueset : set
        The set of all aliases.

    Example
    -------
    >>> Alias('a', 'b').valueset
    {'a', 'b'}
    >>> Alias(['a', 'b']).valueset
    {'a', 'b'}
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



class AliasEnum( Mixin, aenum.Enum ):
    """
    Enum class supporting aliases for members.

    Allows multiple names to reference the same enum member, enabling
    flexible lookups by alias, name, or member.

    Methods
    -------
    get(aliasOrMember)
        Get member by alias, name, or member instance.
    tryGet(aliasOrMember, default=None)
        Like get() but returns default instead of raising.
    toMapping(attr='value')
        Create a dict mapping all aliases to member values.

    Example
    -------
    >>> class Protocol(AliasEnum):
    ...     HTTP = 80, Alias('http', 'web')
    ...     HTTPS = 443, Alias('https', 'secure')
    ...     SSH = 22
    >>>
    >>> Protocol.get('http').value
    80
    >>> Protocol.get('secure').value
    443
    >>> Protocol.HTTP.aliases
    {'HTTP', 'http', 'web'}
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
        """
        Get an enum member by alias, name, or member instance.

        Parameters
        ----------
        aliasOrMember : str or AliasEnum
            The alias, name, or member to look up.

        Returns
        -------
        AliasEnum
            The matching enum member.

        Raises
        ------
        AliasEnumError
            If no member matches the alias.
        """
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
        """
        Create a mapping from all aliases to member attribute values.

        Parameters
        ----------
        attr : str, default='value'
            The attribute to use as the mapping value.

        Returns
        -------
        dict
            Dictionary mapping all aliases (including names) to values.
        """
        mapping = {}
        for name, member in cls.__members__.items():
            member = getattr( cls, name )
            value  = getattr( member, attr )
            for key in [ name ] + sorted(member.aliases):
                mapping[ key ] = value
        return mapping

    @classmethod
    def tryGet( cls, aliasOrMember, default=None ):
        """
        Get member by alias, returning default if not found.

        Parameters
        ----------
        aliasOrMember : str or AliasEnum
            The alias, name, or member to look up.
        default : Any, optional
            Value to return if not found.

        Returns
        -------
        AliasEnum or default
            The matching member or the default value.
        """
        try:
            return cls.get( aliasOrMember )
        except AliasEnumError:
            return default



class AliasEnumError( Exception ):
    """Exception raised when an alias lookup fails."""
    pass