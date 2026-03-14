import unittest

from pyswark.core.models.uri.base import UriModel
from pyswark.core.models.uri.ext import Ext


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
        expected = '/data/data.csv'
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


class UserAtProtocol( Mixin, unittest.TestCase ):
    """Tests for the ``username@protocol/path`` URI format."""

    URIs = [
        'phb2114@gdrive2/PUBLIC/data.json',
        'burrows.peter.h@gdrive2/tmp/file.csv',
        'pyt3rb@s-gdrive2/keepme.json',
    ]

    def test_username(self):
        for uri, expected in zip( self.URIs, ['phb2114', 'burrows.peter.h', 'pyt3rb'] ):
            with self.subTest( uri=uri ):
                model = UriModel( uri )
                self.assertEqual( model.username, expected )

    def test_host(self):
        for uri, expected in zip( self.URIs, ['gdrive2', 'gdrive2', 's-gdrive2'] ):
            with self.subTest( uri=uri ):
                model = UriModel( uri )
                self.assertEqual( model.host, expected )

    def test_path(self):
        for uri, expected in zip( self.URIs, ['/PUBLIC/data.json', '/tmp/file.csv', '/keepme.json'] ):
            with self.subTest( uri=uri ):
                model = UriModel( uri )
                self.assertEqual( model.path, expected )

    def test_scheme_is_none(self):
        for uri in self.URIs:
            with self.subTest( uri=uri ):
                model = UriModel( uri )
                self.assertIsNone( model.scheme )

    def test_no_path(self):
        model = UriModel( 'phb2114@gdrive2' )
        self.assertEqual( model.username, 'phb2114' )
        self.assertEqual( model.host, 'gdrive2' )
        self.assertIsNone( model.path )

    def test_does_not_affect_standard_user_at_host(self):
        model = UriModel( 'user@domain.com/path' )
        self.assertEqual( model.username, 'user' )
        self.assertEqual( model.host, 'domain.com' )
        self.assertEqual( model.path, '/path' )

    def test_does_not_affect_bare_relative_path(self):
        model = UriModel( 'path/to/file' )
        self.assertIsNone( model.username )
        self.assertIsNone( model.host )


class ExtTests( unittest.TestCase ):

    def test_ext_full(self):
        e = Ext( 'file.csv.gz' )
        self.assertEqual( e.full, 'csv.gz' )

    def test_ext_root(self):
        e = Ext( 'file.csv.gz' )
        self.assertEqual( e.root, 'csv' )

    def test_ext_absolue(self):
        e = Ext( 'file.csv.gz' )
        self.assertEqual( e.absolute, 'gz' )

