from pyswark.core.datahandler import base
from pyswark.core.models.uri.base import UriModel


def fixUri(fun):
    """ i.e. google.com --> https://google.com/ """
    def wrapper( self, uri ):
        model = UriModel( uri )
        return fun( self, f'{ model.protocol }:/{ model.tail }')
    return wrapper


class Url(base.AbstractDataHandler):

    @fixUri
    def __init__( self, uri ):
        super().__init__( uri )

    def _read( self, fp, **kw ):
        return fp.read( **kw )
