import re
import enum as _enum

class Mixin:

    @classmethod
    def asDict(cls):
        """ return a dict of the enum members and their values """
        return { k: member.value for k, member in cls.__members__.items() }
    
    @classmethod
    def asPythonCode( cls, name="" ):
        """ return the enum as a python code string """
        
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
        """ create an enum dynamically from a dict of members """
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
    pass