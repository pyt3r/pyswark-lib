class TypeCheck:

    @classmethod
    def checkIfAllowedType( cls, base, allowed=None ):
        base = cls.importType( base )
        allowed = allowed or []
        allowed = allowed if isinstance( allowed, list ) else [ allowed ]
        match = [ cls.isSameType( base, a ) for a in allowed ]
        if allowed and not any( match ):
            raise ValueError( f"type={ base } is not an allowed type: {allowed=}" )

    @classmethod
    def checkIfAllowedSubType( cls, base, allowed=None ):
        base = cls.importType( base )
        allowed = allowed or []
        allowed = allowed if isinstance( allowed, list ) else [ allowed ]
        match = [ cls.isSubclass( base, a ) for a in allowed ]
        if allowed and not any( match ):
            raise ValueError( f"type={ base } is not an allowed subclass: {allowed=}" )

    @classmethod
    def checkIfAllowedInstance( cls, obj, allowed=None ):
        allowed = allowed or []
        allowed = allowed if isinstance( allowed, list ) else [ allowed ]
        match = [ cls.isInstance( obj, a ) for a in allowed ]
        if allowed and not any( match ):
            raise ValueError( f"object={ obj } is not an allowed instance: {allowed=}" )

    @classmethod
    def isSameType( cls, one, other ):
        one   = cls.importType( one )
        other = cls.importType( other )
        return one == other

    @classmethod
    def checkIfSubclass( cls, one, other ):
        if not cls.isSubclass( one, other ):
            raise ValueError( f"type={ one } is not a subclass of { other }" )

    @classmethod
    def isSubclass( cls, one, other ):
        one   = cls.importType( one )
        other = cls.importType( other )
        return issubclass( one, other )

    @classmethod
    def checkIfInstance( cls, obj, klass ):
        if not cls.isInstance( obj, klass ):
            raise ValueError( f"object={ obj } is not an instance of { klass }" )

    @classmethod
    def isInstance( cls, obj, klass ):
        klass = cls.importType( klass )
        return isinstance( obj, klass )

    @staticmethod
    def importType( klass ):
        from pyswark.core.io import api
        
        if isinstance( klass, str ):
            return api.read( klass, datahandler='python' )
        klass = klass if isinstance( klass, type ) else type( klass )
        return klass

