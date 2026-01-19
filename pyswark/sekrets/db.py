from pyswark.core.io import api
from pyswark.core.models import db # note the change from gluedb to core.models
from pyswark.sekrets.models import base, generic


class Db( db.Db ):
    AllowedInstances = [ base.Sekret ]

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
                obj = api.read( obj, datahander='string' )
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
                obj = generic.Sekret( **obj )
                success = True
            except:
                success = False

        return success, obj, name
