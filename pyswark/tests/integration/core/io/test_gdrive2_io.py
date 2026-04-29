import unittest
from uuid import uuid4

from pyswark.core.io import api
from pyswark.core.io.base import CannotOverwrite
from pyswark.core.io.iohandler import IoHandler


USER       = 'phb2114'
KEEPME_URI = f'gdrive2://@{ USER }/{ USER }-keepme.json'


def _scratchUri():
    return f'gdrive2://@{ USER }/pyswark-integration-test-{ uuid4().hex }.txt'


def _tryCleanup( uri ):
    try:
        handler = IoHandler( uri=uri ).acquire()
        if handler.exists():
            handler.rm()
    except Exception:
        pass


def _canWrite():
    """Probe writability — service-account creds get 403 from Google even though
    reads work. Skip the write suite in that case rather than fail noisily."""
    uri = _scratchUri()
    try:
        api.write( 'probe', uri )
    except Exception as exc:
        return False, str( exc )

    _tryCleanup( uri )
    return True, None


_CAN_WRITE, _WRITE_BLOCKER = _canWrite()


class TestGDrive2IoIntegration( unittest.TestCase ):
    """
    Smoke test for reading via pyswark.core.io.api using a gdrive2 URI.

    No assertions are made; the test simply exercises the path and will
    fail if the integration is broken.
    """

    def test_api_read_gdrive2_uri( self ):
        api.read( KEEPME_URI )


@unittest.skipUnless( _CAN_WRITE, f"gdrive2 writes unavailable for { USER }: { _WRITE_BLOCKER }" )
class TestGDrive2IoWriteIntegration( unittest.TestCase ):
    """End-to-end write/read/overwrite/rm against live gdrive2 via pyswark.core.io.api."""

    def setUp( self ):
        self.uri     = _scratchUri()
        self.payload = f'pyswark io.write test { uuid4() }'
        self.addCleanup( _tryCleanup, self.uri )

    def test_api_write_then_read_roundtrip( self ):
        api.write( self.payload, self.uri )
        self.assertEqual( api.read( self.uri ), self.payload )

    def test_api_write_refuses_to_clobber_without_overwrite( self ):
        api.write( self.payload, self.uri )
        with self.assertRaises( CannotOverwrite ):
            api.write( 'second attempt', self.uri )

        self.assertEqual( api.read( self.uri ), self.payload )

    def test_api_write_overwrite_replaces_existing( self ):
        api.write( self.payload, self.uri )
        new_payload = 'overwritten content'
        api.write( new_payload, self.uri, overwrite=True )

        self.assertEqual( api.read( self.uri ), new_payload )

    def test_iohandler_rm_removes_file( self ):
        api.write( self.payload, self.uri )
        handler = IoHandler( uri=self.uri ).acquire()
        self.assertTrue( handler.exists() )

        handler.rm()
        self.assertFalse( handler.exists() )


if __name__ == '__main__':
    unittest.main()
