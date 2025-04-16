from pyswark.core.models.uri import root_all


class ExtDescriptor:

    def __get__(self, obj, objtype=None):
        klass  = self._getKlass( obj.model )
        handle = getattr( self, klass.EXT_HANDLER )
        return handle( obj )

    def _getKlass( self, model ):
        for klass in root_all.get():
            if isinstance( model.root, klass ):
                return klass
        raise TypeError( f"Cannot find handle for model={ model }" )
