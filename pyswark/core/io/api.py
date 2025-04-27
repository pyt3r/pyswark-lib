from pyswark.core.io import guess as _guess
from pyswark.core.io.datahandler import DataHandler


def read( uri, datahandler=None, **kw ):
    handler = acquire( uri, datahandler )
    return handler.read( **kw )


def write( data, uri, datahandler=None, **kw ):
    handler = acquire( uri, datahandler )
    return handler.write( data, **kw )


def acquire( uri, datahandler=None ):
    if not datahandler:
        klass = guess( uri )
    else:
        klass = DataHandler.get(datahandler)
    return klass( uri )


def guess( uri ):
    return _guess.api( uri )