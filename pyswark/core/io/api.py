from pyswark.core.io.contents import Contents


def read( uri, datahandler=None, **kw ):
    contents = Contents( uri=uri, datahandler=datahandler, kw=kw )
    return contents.read()


def write( data, uri, datahandler=None, **kw ):
    contents = Contents( uri=uri, datahandler=datahandler, kw=kw )
    return contents.write( data )


def acquire( uri, datahandler=None ):
    contents = Contents( uri=uri, datahandler=datahandler )
    return contents.acquire()
