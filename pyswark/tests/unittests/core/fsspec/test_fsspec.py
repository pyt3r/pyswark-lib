import unittest

from unittest.mock import patch, MagicMock

from pyswark.core.fsspec import fix


MOCK_SEKRET = {
    "path": "/root/drive",
    "client_id": "abc",
    "client_secret": "xyz",
}


class TestfsspecFilesystem( unittest.TestCase ):
    """fsspec.filesystem should delegate through fix.filesystem to the underlying fsspec.filesystem."""

    @patch( 'pyswark.core.fsspec.fsspec.filesystem' )
    @patch( 'pyswark.core.fsspec.fix.sekrets_api' )
    def test_filesystem_with_target_username(self, mock_api, mock_fs):
        mock_api.get.return_value = MOCK_SEKRET
        mock_fs.return_value = MagicMock()

        from pyswark.core.fsspec import fsspec
        fsspec.filesystem( 'gdrive2', target_username='alice' )

        # We at least expect delegation with the right protocol and username;
        # exact sekret lookup behavior is covered in fix tests.
        mock_fs.assert_called_once()
        args, kwargs = mock_fs.call_args
        self.assertEqual( args[0], 'gdrive2' )
        self.assertEqual( kwargs.get( 'target_username' ), 'alice' )

    @patch( 'pyswark.core.fsspec.fsspec.filesystem' )
    def test_filesystem_plain(self, mock_fs):
        mock_fs.return_value = MagicMock()

        from pyswark.core.fsspec import fsspec
        fsspec.filesystem( 'file' )

        # For plain filesystem calls, we just forward the protocol.
        mock_fs.assert_called_once_with( 'file' )
