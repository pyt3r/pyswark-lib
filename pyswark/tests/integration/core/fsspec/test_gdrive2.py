import unittest
from uuid import uuid4

from pyswark.core import fsspec


USER       = 'phb2114'
KEEPME_URI = f'gdrive2://@{ USER }/{ USER }-keepme.json'


def _scratchPair():
    """Return ``(uri, name)`` pointing at a unique scratch path at the sekret
    root. The name is relative (for ``fs.exists/rm/open``) and the URI is
    absolute (for ``fsspec.open``). Tests own cleanup."""
    name = f'pyswark-integration-test-{ uuid4().hex }.txt'
    uri  = f'gdrive2://@{ USER }/{ name }'
    return uri, name


def _canWrite():
    """
    Probe whether the active credential can actually upload. Service-account
    creds (the common case for CI) get a 403 ``quotaExceeded`` from Google
    even though reads work fine — in that case we skip the write suite rather
    than fail noisily. Run-local / user-OAuth creds sail through.
    """
    uri, name = _scratchPair()
    try:
        with fsspec.open( uri, 'wb' ) as f:
            f.write( b'probe' )
    except Exception as exc:
        return False, str( exc )

    try:
        fsspec.filesystem( 'gdrive2', target_username=USER ).rm( name )
    except Exception:
        pass

    return True, None


_CAN_WRITE, _WRITE_BLOCKER = _canWrite()


@unittest.skipUnless( _CAN_WRITE, f"gdrive2 writes unavailable for { USER }: { _WRITE_BLOCKER }" )
class TestGDrive2WriteIntegration( unittest.TestCase ):
    """End-to-end write/read/delete against live gdrive2 via pyswark.core.fsspec."""

    def setUp( self ):
        self.uri, self.name = _scratchPair()
        self.payload        = f'pyswark write test { uuid4() }'.encode()
        self.fs             = fsspec.filesystem( 'gdrive2', target_username=USER )
        self.addCleanup( self._cleanup )

    def _cleanup( self ):
        try:
            if self.fs.exists( self.name ):
                self.fs.rm( self.name )
        except Exception:
            pass

    def test_write_then_read_roundtrip( self ):
        with fsspec.open( self.uri, 'wb' ) as f:
            f.write( self.payload )

        with fsspec.open( self.uri, 'rb' ) as f:
            got = f.read()

        self.assertEqual( got, self.payload )

    def test_exists_flips_true_then_false_after_rm( self ):
        self.assertFalse( self.fs.exists( self.name ) )

        with fsspec.open( self.uri, 'wb' ) as f:
            f.write( self.payload )

        self.assertTrue( self.fs.exists( self.name ) )

        self.fs.rm( self.name )
        self.assertFalse( self.fs.exists( self.name ) )

    def test_filesystem_open_with_root_relative_path( self ):
        """Mirrors the read-only sibling test but for writes: ``fs.open`` with
        a path relative to the sekret root should resolve correctly on write."""
        with self.fs.open( self.name, 'wb' ) as f:
            f.write( self.payload )

        with self.fs.open( self.name, 'rb' ) as f:
            self.assertEqual( f.read(), self.payload )


class TestGDrive2Integration( unittest.TestCase ):
    """
    Smoke tests for the gdrive2 integration.

    These are not asserting on content; they just exercise the
    end-to-end wiring so that they fail loudly if the integration
    breaks.
    """

    def test_open_via_core_fsspec( self ):
        """Ensure we can open a file via pyswark.core.fsspec."""
        with fsspec.open( KEEPME_URI ) as f:
            _ = f.read()

    def test_filesystem_walk_and_open( self ):
        """Ensure filesystem(), walk(), and fs.open() work together."""
        fs = fsspec.filesystem( 'gdrive2', target_username=USER )

        for _root, _dirs, _files in fs.walk( fs.path ):
            break

        with fs.open( f'{ USER }-keepme.json' ) as f:
            _ = f.read()


if __name__ == '__main__':
    unittest.main()
