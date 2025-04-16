from pyswark.core.models.uri.root import Http, FileRelative, FileAbsolute
from pyswark.core.models.uri.root_resolvable import Resolvable
from pyswark.core.models.uri import schemes


class ResolvableHttp( Resolvable ):
    EXT_HANDLER = 'http'

    _STARTSWITH = [ f'{ e }.' for e in [ 'www', ] ]
    _ENDSWITH   = [ f'.{ e }' for e in [
        'com', 'net', 'org', 'co', 'us', 'ai', 'gov', 'site', 'me', 'ly', 'info',
        'html', 'shtml', ]
                    ]
    _CONTAINS   = [ f'{e}/' for e in _ENDSWITH ]

    @staticmethod
    def _resolve( root ):
        return Http(f"http:{ root }")


class ResolvableFile( Resolvable ):
    EXT_HANDLER = 'file'

    _NOTSTARTSWITH = [ f'{ s }:' for s in schemes.ALLOWED]

    @staticmethod
    def _resolve( root: str ):
        sep   = '/'
        isAbs = root.startswith( sep )

        # -- fixes '//path/to/file' --> 'path/to/file'
        while root and root.startswith( sep ) and root != sep:
            root = root[1:]

        root  = f'file:{ root }'
        return FileAbsolute(root) if isAbs else FileRelative(root)
