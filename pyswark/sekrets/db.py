from typing import ClassVar
from pyswark.core.io import api
from pyswark.gluedb import db # note the change from gluedb to core.models
from pyswark.sekrets.models import base, generic


class Db( db.Base ):
    FALLBACK : ClassVar[ type[ base.Sekret ] ] = generic.Sekret
    AllowedInstances = [ base.Sekret ]

    def _init( self, fallback=generic.Sekret, **kw ):
        self.FALLBACK = fallback
        return super()._init( *a, **kw )

    @classmethod
    def _post_fallback( cls, obj, name=None ):
        success = False
        success, obj, name = cls._post_fallback_string( obj, name, success )
        success, obj, name = cls._post_fallback_generic( obj, name, success )
        return obj, name

    @classmethod
    def _post_fallback_string( cls, obj, name=None, success=False ):
        if isinstance( obj, str ):
            try:
                tmp = api.read( obj, 'string' )

                success = False
                if isinstance( tmp, ( list, tuple ) ):
                    if len( tmp ) == 1:
                        obj = tmp[0]
                        success = True
                else:
                    obj = tmp
                    success = True
                
            except:
                success = False
        return success, obj, name

    @classmethod
    def _post_fallback_generic( cls, obj, name=None, success=False ):

        if isinstance( obj, dict ):
            name = obj.get( 'name', name )

            try:
                obj = { k: v for k, v in obj.items() if k != 'name' }
                obj = cls.FALLBACK( **obj )
                success = True
            except:
                success = False

        return success, obj, name
