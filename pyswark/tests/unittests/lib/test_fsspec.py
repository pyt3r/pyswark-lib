import unittest
from pyswark.lib import fsspec


PYTHON_DATA = [1,2,3]


class FsTests( unittest.TestCase ):

    def test_python_fs(self):
        fs = fsspec.filesystem("python")

        path = "pyswark.tests.unittests.lib.test_fsspec.PYTHON_DATA"
        with fs.open( path ) as f:
            pythonData = f.locate()

        self.assertListEqual( PYTHON_DATA, pythonData )

        uri = f"python://{ path }"
        with fsspec.open( uri ) as f:
            pythonData = f.locate()

        self.assertListEqual( PYTHON_DATA, pythonData )
