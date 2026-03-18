import unittest
from pathlib import Path
from unittest.mock import patch

import pyswark
from pyswark.core.fsspec import fix
from pyswark.core.fsspec.fix import Handler, Gdrive2, Pyswark


MOCK_SEKRET = {
    'path': '/root/drive',
    'client_id': 'abc',
    'client_secret': 'xyz',
}


class TestHandlerConstruction( unittest.TestCase ):
    """Handler should parse URIs and normalise scheme/username."""

    def test_from_uri_with_username(self):
        h = Handler( uri='gdrive2://@alice/some/file.csv' )
        self.assertEqual( h.scheme, 'gdrive2' )
        self.assertEqual( h.username, 'alice' )

    def test_from_uri_without_username(self):
        h = Handler( uri='http://example.com/data.csv' )
        self.assertEqual( h.scheme, 'http' )
        self.assertEqual( h.username, '' )

    def test_from_scheme_and_username_only(self):
        h = Handler( scheme='S3', username='Bob' )
        self.assertEqual( h.scheme, 's3' )
        self.assertEqual( h.username, 'bob' )

    def test_uri_overrides_scheme_and_username(self):
        h = Handler( uri='gdrive2://@alice/f.txt', scheme='other', username='other' )
        self.assertEqual( h.scheme, 'other' )
        self.assertEqual( h.username, 'other' )

    def test_none_defaults(self):
        h = Handler( scheme='s3' )
        self.assertIsNone( h.uri )
        self.assertEqual( h.username, '' )

    def test_getPath(self):
        h = Handler( uri='s3://@bob/data/file.csv' )
        self.assertEqual( h.getPath(), Path( '/data/file.csv' ) )


class TestHandlerGetHandler( unittest.TestCase ):

    def test_raises_when_no_args(self):
        with self.assertRaises( ValueError ):
            Handler.getHandler()

    def test_returns_base_handler_for_unknown_scheme(self):
        h = Handler.getHandler( scheme='s3', username='alice' )
        self.assertIsNone( h )

    def test_dispatches_to_gdrive2(self):
        h = Handler.getHandler( uri='gdrive2://@alice/file.csv' )
        self.assertIsInstance( h, Gdrive2 )

    def test_base_getSekret_returns_empty(self):
        h = Handler.getHandler( scheme='pyswark' )
        self.assertEqual( h.getSekret(), {} )


class TestGdrive2( unittest.TestCase ):

    @patch.object( Gdrive2, '_getSekret', return_value=MOCK_SEKRET )
    def test_getSekret_returns_full_creds(self, _):
        h = Gdrive2( uri='gdrive2://@alice/file.csv' )
        sekret = h.getSekret()
        self.assertIn( 'path', sekret )
        self.assertIn( 'client_id', sekret )

    @patch.object( Gdrive2, '_getSekret', return_value=MOCK_SEKRET )
    def test_getPath_joins_root_and_relative(self, _):
        h = Gdrive2( uri='gdrive2://@alice/sub/file.csv' )
        result = h.getPath()
        self.assertEqual( result, Path( '/root/drive/sub/file.csv' ) )

    @patch.object( Gdrive2, '_getSekret', return_value={ 'client_id': 'abc' } )
    def test_getPath_no_root_in_sekret(self, _):
        """When sekret has no 'path' key, root defaults to empty string."""
        h = Gdrive2( uri='gdrive2://@alice/file.csv' )
        result = h.getPath()
        self.assertEqual( result, Path( 'file.csv' ) )


class TestOpenDecorator( unittest.TestCase ):

    @patch.object( Gdrive2, '_getSekret', return_value=MOCK_SEKRET )
    def test_injects_protocol_and_creds(self, _):
        calls = []

        @fix.open
        def fake_open( uri, *args, **kwargs ):
            calls.append( ( uri, args, kwargs ) )

        fake_open( 'gdrive2://@alice/sub/file.csv', 'rb' )
        self.assertEqual( len( calls ), 1 )
        uri, args, kwargs = calls[0]

        self.assertIsInstance( uri, Path )
        self.assertIn( 'sub/file.csv', str( uri ) )
        self.assertEqual( args, ( 'rb', ) )
        self.assertEqual( kwargs['protocol'], 'gdrive2' )
        self.assertEqual( kwargs['client_id'], 'abc' )


class TestFilesystemDecorator( unittest.TestCase ):

    @patch( 'pyswark.core.fsspec.fix.sekrets_api' )
    def test_injects_creds_for_target_username(self, mock_api):
        mock_api.get.return_value = MOCK_SEKRET
        calls = []

        @fix.filesystem
        def fake_fs( protocol, **kwargs ):
            calls.append( ( protocol, kwargs ) )

        fake_fs( 'gdrive2', target_username='alice' )
        protocol, kwargs = calls[0]
        self.assertEqual( protocol, 'gdrive2' )
        self.assertEqual( kwargs['client_id'], 'abc' )

    def test_no_injection_without_target_username(self):
        calls = []

        @fix.filesystem
        def fake_fs( protocol, **kwargs ):
            calls.append( ( protocol, kwargs ) )

        fake_fs( 's3', bucket='my-bucket' )
        _, kwargs = calls[0]
        self.assertIn( 'bucket', kwargs )
        self.assertNotIn( 'client_id', kwargs )


class TestPyswark( unittest.TestCase ):
    """Tests for the pyswark:// fix handler and filesystem."""

    def test_dispatches_to_pyswark_handler(self):
        h = Handler.getHandler( uri='pyswark://data/df.csv' )
        self.assertIsInstance( h, Pyswark )

    def test_getPath_returns_absolute(self):
        import pyswark
        h = Pyswark( uri='pyswark:///data/df.csv', scheme='pyswark' )
        expected = Path( pyswark.__file__ ).parent / 'data/df.csv'
        self.assertEqual( h.getPath(), expected )

    def test_getSekret_returns_empty(self):
        h = Pyswark( uri='pyswark://data/df.csv' )
        self.assertEqual( h.getSekret(), {} )

    def test_open_decorator_resolves_pyswark_uri(self):
        import pyswark
        calls = []

        @fix.open
        def fake_open( uri, *args, **kwargs ):
            calls.append( ( uri, kwargs ) )

        fake_open( 'pyswark://data/df.csv' )
        uri, kwargs = calls[0]
        self.assertIsInstance( uri, Path )
        expected = Path( pyswark.__file__ ).parent / 'data/df.csv'
        self.assertEqual( uri, expected )
        self.assertEqual( kwargs['protocol'], 'pyswark' )

