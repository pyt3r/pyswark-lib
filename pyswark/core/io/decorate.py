import functools
from pyswark.util.log import logger


class AbstractDecorator:
    PAYLOAD = {}

    def __init__( self, mode ):
        attr = "PAYLOAD"
        assert hasattr( self, attr ), f"Must specify class attribute '{ attr }'"
        self._mode = mode

    @property
    def payload( self ):
        return self.PAYLOAD[ self._mode ]


class Kwargs( AbstractDecorator ):

    def __init__( self, name, mode ):
        super().__init__( mode )
        self._name = name

    @property
    def payload( self ):
        return self.PAYLOAD[ self._name ][ self._mode ]

    @classmethod
    def decorate( cls, mode ):
        """ decorator factory for applying default kwargs """

        def decorator(func):

            @functools.wraps(func)
            def wrapper( slf, *a, **kw ):
                name = slf.__class__.__name__
                o    = cls( name, mode )
                kw   = kw or o.payload
                return func( slf, *a, **kw )

            return wrapper
        return decorator


class Log( AbstractDecorator ):

    @classmethod
    def decorate( cls, mode ):
        """ decorator factory for logger """

        def decorator(func):

            @functools.wraps(func)
            def wrapper( slf, *a, **kw ):
                o = cls( mode )
                msg = f"{ o.payload } uri='{slf.uri.inputs.uri}'..."
                logger.info( msg )
                result = func( slf, *a, **kw )
                logger.info( "done." )
                return result

            return wrapper
        return decorator
