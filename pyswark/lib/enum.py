"""
Enum Utilities
==============

This module provides enhanced enum classes with additional utility methods
for introspection, code generation, and dynamic enum creation.

Classes
-------
Enum
    Enhanced enum with utility methods (asDict, asPythonCode, createDynamically).
Mixin
    Mixin class providing utility methods for enums.
"""

import re
import enum as _enum

class Mixin:
    """
    Mixin providing utility methods for enum classes.

    Methods
    -------
    asDict()
        Return a dict mapping member names to values.
    asPythonCode(name)
        Generate Python code to recreate the enum.
    createDynamically(enumMembers, enumName)
        Create an enum dynamically from a dict.
    """

    @classmethod
    def asDict(cls):
        """
        Return a dict mapping member names to values.

        Returns
        -------
        dict
            Dictionary with member names as keys and values as values.

        Example
        -------
        >>> class Status(Enum):
        ...     ACTIVE = 1
        ...     INACTIVE = 0
        >>> Status.asDict()
        {'ACTIVE': 1, 'INACTIVE': 0}
        """
        return { k: member.value for k, member in cls.__members__.items() }
    
    @classmethod
    def asPythonCode( cls, name="" ):
        """
        Generate Python code to recreate the enum.

        Parameters
        ----------
        name : str, optional
            Name for the generated class. Defaults to ``My{ClassName}``.

        Returns
        -------
        str
            Python source code string.
        """
        
        base = f"{ cls.__module__}.{ cls.__name__ }"
            
        className = base
        importStmt = f"import { base }"

        moduleName, className = base.rsplit(".", 1)
        importStmt = f"from {moduleName} import {className}"

        if not name:
            name = f"My{className}"

        membersAsCode = "\n".join( [ f"    {k} = {v}" for k, v in cls.asDict().items() ] )
        classAsCode = f"class {name}( {className} ):\n{ membersAsCode }"

        return f"{ importStmt }\n\n{ classAsCode }"

    @classmethod
    def createDynamically( cls, enumMembers, enumName=''):
        """
        Create an enum dynamically from a dict of members.

        Parameters
        ----------
        enumMembers : dict
            Dictionary mapping member names to values.
        enumName : str, optional
            Name for the new enum class.

        Returns
        -------
        Enum
            A new enum class with the specified members.

        Example
        -------
        >>> MyEnum = Enum.createDynamically({'A': 1, 'B': 2}, 'MyEnum')
        >>> MyEnum.A.value
        1
        """
        if not enumName:
            enumName = cls.__name__

        newMembers = {}
        for k, v in enumMembers.items():
            if k in newMembers:
                raise ValueError( f"Member {k} already exists in enum {enumName}" )
            newMembers[ cls._toValidName(k) ] = v

        return cls( enumName, newMembers )

    @staticmethod
    def _toValidName( name ):
        """ convert a name to a valid python name """
        validName = str(name)
        replacement = '_'

        if not re.match( r'^[a-zA-Z_]', validName ):
            validName = replacement + validName

        validName = re.sub( r'\W|^(?=\d)', replacement, validName )

        while validName.startswith( replacement*2 ):
            validName = validName[1:]

        return validName
    

class Enum( Mixin, _enum.Enum ):
    """
    Enhanced enum with utility methods.

    Extends Python's built-in Enum with additional methods for
    introspection and code generation.

    Example
    -------
    >>> from pyswark.lib.enum import Enum
    >>>
    >>> class Status(Enum):
    ...     ACTIVE = 1
    ...     INACTIVE = 0
    >>>
    >>> Status.asDict()
    {'ACTIVE': 1, 'INACTIVE': 0}
    """
    pass