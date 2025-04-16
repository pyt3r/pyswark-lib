import pathlib
from typing import ClassVar
from pydantic import RootModel, field_validator

from swark.lib.pydantic.uri.annotated_url import AnnotatedUrl


class UriRootModel( RootModel ):
    root        : AnnotatedUrl()
    EXT_HANDLER : ClassVar[ str ] = ""

    @field_validator( 'root', mode='before' )
    @classmethod
    def _clean( cls, root: str ) -> str:
        if not isinstance(root, str):
            return root
        return root.replace( '\\', '/' )

    def toString(self):
        return f'{ self.protocol }{ self.delim }{ self.tail }'

    @property
    def url(self):

        from pyswark.core.models.uri import root_resolvable

        root = self.root
        if isinstance( root, root_resolvable.Resolvable ):
            root = root.root
        return root

    @property
    def delim(self):
        return ':/' if self.protocol != 'python' else '://'

    @property
    def tail(self):
        return str(self.url.root).split( self.delim )[-1]

    @property
    def protocol(self):
        return self.url.scheme

    @property
    def protocols(self):
        return [ self.protocol ]

    @property
    def scheme(self):
        return self.url.scheme

    @property
    def host(self):
        return self.url.host

    @property
    def username(self):
        return self.url.username

    @property
    def password(self):
        return self.url.password

    @property
    def Path(self):
        path = self.url.path
        if not path:
            return path

        sep = '/'
        while path and path.endswith( sep ) and path != sep:
            path = path[:-1]

        head, *tails = path.split( sep )
        Path = pathlib.Path( head )
        for tail in tails:
            Path = Path / tail

        return Path

    @property
    def path(self):
        if self.Path:
            return self.Path.as_posix()

    @property
    def Ext(self):
        from pyswark.core.models.uri import ext

        return ext.Ext( model=self )

    @property
    def ext(self):
        return self.Ext.root

    @property
    def ext_root(self):
        Path = self.Path
        if Path:
            return

    @property
    def ext_original(self):
        return

    @property
    def ext_full(self):
        return


class FileAbsolute( UriRootModel ):
    """ file with absolute path """
    root: AnnotatedUrl( allowed_schemes=['file'] )
    EXT_HANDLER = 'file'


class FileRelative( UriRootModel ):
    """ file with relative path """
    root: AnnotatedUrl( allowed_schemes=['file'] )
    EXT_HANDLER = 'file'


class Python( UriRootModel ):
    root: AnnotatedUrl( allowed_schemes=['python'] )
    EXT_HANDLER = 'python'


class Http( UriRootModel ):
    root: AnnotatedUrl( allowed_schemes=['http', 'https'] )
    EXT_HANDLER = 'http'
