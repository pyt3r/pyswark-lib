import unittest

from pyswark.core.models.uri.base import UriModel


class _UriMixin:

    URIs = []

    def runTests( self, attr, expected, uris=None ):
        uris = uris or self.URIs

        models = [
            UriModel(u) for u in uris
        ]
        for i, model in enumerate( models ):
            with self.subTest( i=i, model=model ):
                self.assertEqual( expected, getattr( model, attr ) )


class UriFileTests( _UriMixin, unittest.TestCase ):
    URIs = [
        '\\x.py//',
        'x.py//',
        'x.py\\\\',
        'x.py/',
        'x.py',
        '/x.py//',
        '/x.py/',
        '/x.py',
        '//x.py//',
        '//x.py/',
        '//x.py',
        '///x.py',
        '////x.py',
        '/////x.py',
        'file:/x.py//',
        'file:/x.py/',
        'file:/x.py',
        'file:///x.py',
        'file:///x.py',
        'file:////x.py',
        'file://///x.py',
    ]

    def test_path(self):
        self.runTests( attr='path', expected='x.py' )

    def test_path2(self):
        uris = [ 'file://x.py', ]
        self.runTests( attr='path', expected='.', uris=uris )

    def test_scheme(self):
        self.runTests( attr='scheme', expected="file" )


class UriPythonTests( _UriMixin, unittest.TestCase ):
    URIs = [
        'python:\\path.to.my.Class\\',
        'python:path.to.my.Class',
        'python:/path.to.my.Class/',
        'python:/path.to.my.Class',
        # 'python://path.to.my.Class',
        'python:///path.to.my.Class',
        'python:////path.to.my.Class',
        'python://///path.to.my.Class',
    ]

    def test_path(self):
        self.runTests( attr='path', expected="path.to.my.Class" )

    def test_path2(self):
        uris = [ 'python://path.to.my.Class', ]
        self.runTests( attr='path', expected=None, uris=uris )

    def test_scheme(self):
        self.runTests( attr='scheme', expected="python" )


class UriHttpTests( _UriMixin, unittest.TestCase ):
    URIs = [
        'website.com/some/endpoint',
        '/website.com/some/endpoint',
        'http:/website.com/some/endpoint',
        'http://website.com/some/endpoint',
        'http:///website.com/some/endpoint',
        'http:////website.com/some/endpoint',
        'http://///website.com/some/endpoint',
    ]

    def test_host(self):
        self.runTests( 'host', "website.com" )

    def test_host2(self):
        uris = [ 'website.com', '/website.com', ]
        self.runTests( 'host', "website.com", uris )

    def test_scheme(self):
        self.runTests( 'scheme', "http" )
        self.runTests( 'protocol', "http" )

    def test_path(self):
        self.runTests( 'path', "some/endpoint" )


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
