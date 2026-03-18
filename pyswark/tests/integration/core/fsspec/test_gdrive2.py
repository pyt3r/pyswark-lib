import unittest

from pyswark.core import fsspec


class TestGDrive2Integration(unittest.TestCase):
    """
    Smoke tests for the gdrive2 integration.

    These are not asserting on content; they just exercise the
    end-to-end wiring so that they fail loudly if the integration
    breaks.
    """

    def test_open_via_core_fsspec(self):
        """Ensure we can open a file via pyswark.core.fsspec."""
        with fsspec.open("gdrive2://@phb2114/phb2114-keepme.json") as f:
            _ = f.read()

    def test_filesystem_walk_and_open(self):
        """Ensure filesystem(), walk(), and fs.open() work together."""
        fs = fsspec.filesystem("gdrive2", target_username="phb2114")

        # Exercise the walk iterator at least once.
        for _root, _dirs, _files in fs.walk(fs.path):
            break

        # And that we can open a file relative to the root.
        with fs.open("phb2114-keepme.json") as f:
            _ = f.read()

