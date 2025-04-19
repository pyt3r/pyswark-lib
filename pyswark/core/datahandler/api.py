from pyswark.core.models.uri.base import UriModel
from pyswark.core.datahandler import registry
from pyswark.core.datahandler.registry import Handler


def read( uri, datahandler=None, **kw ):
    handler = acquire( uri, datahandler )
    return handler.read( **kw )


def write( data, uri, datahandler=None, **kw ):
    handler = acquire( uri, datahandler )
    return handler.write( data, **kw )


def acquire( uri, datahandler=None ):
    if not datahandler:
        datahandler = _guess( uri )
    return _acquire( uri, datahandler )


def _acquire( uri, datahandler ):
    return registry.get(datahandler)(uri)


def _guess( uri ):
    uri    = UriModel( uri )
    ext    = uri.Ext
    scheme = uri.scheme

    guess = BY_EXT.get( ext.full ) if scheme != 'python' else None
    guess = guess or BY_EXT.get( ext.absolute )
    guess = guess or BY_SCHEME.get( scheme, scheme )
    assert guess, f"Handler not found for {uri=}"
    return guess


# == guesses based on criteria embedded in the uri ==

BY_EXT = {
    'csv'       : Handler.DF_CSV,
    'csv.gz'    : Handler.DF_CSV_GZ,
    'parquet'   : Handler.DF_PARQUET,
    'json'      : Handler.JSON,
    'pjson'     : Handler.PJSON,
    'gluedb'    : Handler.GLUEDB,
}
BY_EXT.update({ e: Handler.YAML_DOC for e in [ 'yaml', 'yml', 'doc.yaml', 'doc.yml' ] })
BY_EXT.update({ e: Handler.YAML_DOCS for e in [ 'docs.yaml', 'docs.yml' ] })
BY_EXT.update({ e: Handler.TEXT for e in [ 'html', 'shtml', 'py', 'txt', 'text', 'tex' ] })

BY_SCHEME = {
    p : Handler.URL for p in [ 'http', 'https' ]
}
BY_SCHEME.update({
    'python' : Handler.PYTHON,
})