from pyswark.core.io.contents import Contents
from pyswark.core.io import guess


def read( uri, datahandler=None, **kw ):
    contents = Contents( uri=uri, datahandler=datahandler, kw=kw )
    return contents.read()


def write( data, uri, datahandler=None, **kw ):
    contents = Contents( uri=uri, datahandler=datahandler, kw=kw )
    return contents.write( data )


def acquire( uri, datahandler=None ):
    contents = Contents( uri=uri, datahandler=datahandler )
    return contents.acquire()


def isUri( uri ):
    """ checks if the uri is a valid uri """
    try:
        guess.api( uri )
        return True
    except ValueError:
        return False