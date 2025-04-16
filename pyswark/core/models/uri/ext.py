from pyswark.core.models.uri import ext_desc


class ExtPath( ext_desc.ExtDescriptor ):

    @staticmethod
    def file( obj ):
        return obj.model.path

    @staticmethod
    def python( obj ):
        return None

    @staticmethod
    def http( obj ):
        return obj.model.path


class ExtFull( ext_desc.ExtDescriptor ):

    @classmethod
    def file( cls, obj ):
        return cls._helper( obj.path )

    @staticmethod
    def python( obj ):
        return None

    @classmethod
    def http( cls, obj ):
        return cls._helper( obj.path )

    @staticmethod
    def _helper( path ):
        *filepath, filename = path.split("/")
        name, *ext = filename.split('.')
        return ".".join( ext )


class ExtRoot( ext_desc.ExtDescriptor ):

    @classmethod
    def file( cls, obj ):
        return cls._helper( obj.full )

    @staticmethod
    def python( obj ):
        return None

    @classmethod
    def http( cls, obj ):
        return cls._helper( obj.full )

    @staticmethod
    def _helper( full ):
        root, *tail = full.split(".")
        return root


class ExtAbsolute( ext_desc.ExtDescriptor ):

    @classmethod
    def file( cls, obj ):
        return cls._helper( obj.full )

    @staticmethod
    def python( obj ):
        return None

    @classmethod
    def http( cls, obj ):
        return cls._helper( obj.full )

    @staticmethod
    def _helper( full ):
        *parts, absolute = full.split(".")
        return absolute


class ExtProtocol( ext_desc.ExtDescriptor ):

    @staticmethod
    def file( obj ):
        return

    @staticmethod
    def python( obj ):
        return None

    @staticmethod
    def http( obj ):
        return


class Ext:

    path     = ExtPath()
    full     = ExtFull()
    root     = ExtRoot()
    absolute = ExtAbsolute()
    protocol = ExtProtocol()

    def __init__(self, model ):
        self.model = model
