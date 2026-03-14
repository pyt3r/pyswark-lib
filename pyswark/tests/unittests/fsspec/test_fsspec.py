import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pyswark.fsspec import fix


MOCK_SEKRET = {
    'path': '/root/drive',
    'client_id': 'abc',
    'client_secret': 'xyz',
}


class TestFsspecOpen( unittest.TestCase ):
    """fsspec.open should delegate through fix.open to _fsspec.open."""

    @patch( 'pyswark.fsspec.fsspec._fsspec' )
    @patch.object( fix.Gdrive2, '_getSekret', return_value=MOCK_SEKRET )
    def test_open_with_credentials(self, _, mock_fsspec):
        mock_fsspec.open.return_value = MagicMock()

        from pyswark.fsspec import fsspec
        fsspec.open( 'gdrive2://@alice/file.csv', 'rb' )

        mock_fsspec.open.assert_called_once()
        call_kwargs = mock_fsspec.open.call_args.kwargs
        self.assertEqual( call_kwargs['protocol'], 'gdrive2' )
        self.assertEqual( call_kwargs['client_id'], 'abc' )

    @patch( 'pyswark.fsspec.fsspec._fsspec' )
    def test_open_plain_uri(self, mock_fsspec):
        mock_fsspec.open.return_value = MagicMock()

        from pyswark.fsspec import fsspec
        fsspec.open( 'http://example.com/data.csv' )

        mock_fsspec.open.assert_called_once()
        call_kwargs = mock_fsspec.open.call_args.kwargs
        self.assertEqual( call_kwargs['protocol'], 'http' )


class TestFsspecFilesystem( unittest.TestCase ):
    """fsspec.filesystem should delegate through fix.filesystem to _fsspec.filesystem."""

    @patch( 'pyswark.fsspec.fsspec._fsspec' )
    @patch( 'pyswark.fsspec.fix.sekrets_api' )
    def test_filesystem_with_target_username(self, mock_api, mock_fsspec):
        mock_api.get.return_value = MOCK_SEKRET
        mock_fsspec.filesystem.return_value = MagicMock()

        from pyswark.fsspec import fsspec
        fsspec.filesystem( 'gdrive2', target_username='alice' )

        mock_fsspec.filesystem.assert_called_once()
        call_kwargs = mock_fsspec.filesystem.call_args.kwargs
        self.assertEqual( call_kwargs['client_id'], 'abc' )

    @patch( 'pyswark.fsspec.fsspec._fsspec' )
    def test_filesystem_plain(self, mock_fsspec):
        mock_fsspec.filesystem.return_value = MagicMock()

        from pyswark.fsspec import fsspec
        fsspec.filesystem( 'file' )

        mock_fsspec.filesystem.assert_called_once_with( 'file', target_username=None )
