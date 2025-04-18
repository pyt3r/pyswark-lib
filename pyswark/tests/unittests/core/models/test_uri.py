import unittest
import pathlib

import pyswark
from pyswark.core.models.uri.base import UriModel


class Mixin:

    URIs = []

    def runTests( self, attr, expected, uris=None ):
        uris = uris or self.URIs

        models = [
            UriModel(u) for u in uris
        ]
        for i, model in enumerate( models ):
            with self.subTest( i=i, model=model ):
                self.assertEqual( expected, getattr( model, attr ) )


class Pyswark( Mixin, unittest.TestCase ):
    URIs = [
        'pyswark:///data/data.csv',
        'pyswark://data/data.csv',
        'pyswark:/data/data.csv',
        'pyswark:data/data.csv',
    ]

    def test_path(self):
        parent   = pathlib.Path( pyswark.__file__ ).parent
        expected = f'{ parent }/data/data.csv'
        self.runTests( attr='path', expected=expected )


class Python( Mixin, unittest.TestCase ):
    URIs = [
        'python:path.to.my.Class',
        'python:/path.to.my.Class',
        'python://path.to.my.Class',
        'python:///path.to.my.Class',
        'python:////path.to.my.Class',
    ]

    def test_path(self):
        self.runTests( attr='path', expected='path.to.my.Class' )



class FileAbsolute( Mixin, unittest.TestCase ):

    URIs = [
        'file-absolute:path/to/file',
        'file-absolute:/path/to/file',
        'file-absolute://path/to/file',
        'file-absolute:///path/to/file',
        'file-absolute:////path/to/file',
        'file:/path/to/file',
        'file://path/to/file',
        'file:///path/to/file',
        'file:////path/to/file',
    ]

    def test_path(self):
        self.runTests( attr='path', expected='/path/to/file' )



class FileRelative( Mixin, unittest.TestCase ):

    URIs = [
        'file-relative:path/to/file',
        'file-relative:/path/to/file',
        'file-relative://path/to/file',
        'file-relative:///path/to/file',
        'file-relative:////path/to/file',
        'file:path/to/file',
    ]

    def test_path(self):
        self.runTests( attr='path', expected='path/to/file' )


class Url( Mixin, unittest.TestCase ):
    URIs = [
        'scheme://username:password@domain.com:8080/my path/to/a page?query=value#section',
        'username:password@domain.com:8080/my path/to/a page',
        'username'       '@domain.com:8080/my path/to/a page',
        'domain.com:8080/my path/to/a page',
        'domain.com'   '/my path/to/a page',
        '/my path/to/a page',
    ]

    def test_path(self):
        self.runTests( attr='path', expected='/my path/to/a page' )


class _ExtMixin:

    URIs = []

    def runTests( self, attr, expected, uris=None ):
        uris = uris or self.URIs

        models = [
            UriModel(u) for u in uris
        ]
        for i, model in enumerate( models ):
            with self.subTest( i=i, model=model ):
                self.assertEqual( expected, getattr( model.Ext, attr ) )


@unittest.skip("temporary skip")
class ExtTests( _ExtMixin, unittest.TestCase ):

    _URI = 'path.path/to.to/x.csv.gz'
    URIs = [
        f'\\{ _URI }/',
        f'{ _URI }//',
        f'{ _URI }\\\\',
        f'{ _URI }/',
        f'{ _URI }',
        f'/{ _URI }//',
        f'/{ _URI }/',
        f'{ _URI }',
    ]

    def test_ext_full(self):
        self.runTests( 'full', 'csv.gz' )

    def test_ext_root(self):
        self.runTests( 'root', 'csv' )

    def test_ext_absolue(self):
        self.runTests( 'absolute', 'gz' )
