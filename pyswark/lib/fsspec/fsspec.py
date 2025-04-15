import fsspec

_PROTOCOLS = {
    'python' : "pyswark.lib.fsspec.implementations.PythonFileSystem",
}
[ fsspec.register_implementation( *_p ) for _p in _PROTOCOLS.items() ]


def open( uri, *args, **kwargs ):
    return fsspec.open( uri, *args, **kwargs )


def filesystem( protocol, **kwargs ):
    """ gets the fs filesystem """
    return fsspec.filesystem( protocol, **kwargs )
