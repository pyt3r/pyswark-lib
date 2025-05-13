import unittest
import os
import tempfile
import shutil
import pandas

from pyswark.lib.pydantic import base
from pyswark.core.io import api, datahandler


class TestCaseLocal( unittest.TestCase ):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree( self.tempdir )


class LocalTestCasesDF( TestCaseLocal ):

    def setUp(self):
        super().setUp()
        self.raw = pandas.DataFrame({'a': [1,2,3]})

    def test_csv(self):
        self._routine( 'df.csv' )

    def test_csv_gz(self):
        self._routine( 'df.csv.gz' )

    def test_parquet(self):
        self._routine( 'df.parquet' )

    def _routine(self, mode, filename=None):
        raw = self.raw
        fn  = filename or mode
        uri = os.path.join( self.tempdir, fn )

        Handler = datahandler.get(mode)
        handler = Handler( uri )

        self.assertFalse( handler.exists() )

        handler.write( raw )
        self.assertTrue( handler.exists() )

        handler = Handler( uri )
        data    = handler.read()

        pandas.testing.assert_frame_equal( raw, data )


class LocalTestCasesJson( TestCaseLocal ):

    def setUp(self):
        super().setUp()
        self.raw = { 'a' : 1, 'b': 2 }

    def test_json(self):
        self._routine( 'json', 'data.json' )

    def _routine(self, mode, filename=None):
        raw = self.raw
        fn  = filename or mode
        uri = os.path.join( self.tempdir, fn )

        Handler = datahandler.get(mode)
        handler = Handler( uri )

        self.assertFalse( handler.exists() )

        handler.write( raw )
        self.assertTrue( handler.exists() )

        handler = Handler( uri )
        data    = handler.read()

        self.assertDictEqual( raw, data )


class LocalTestCasesYamlDoc( TestCaseLocal ):

    def setUp(self):
        super().setUp()
        self.raw = { 'a' : 1, 'b': 2 }

    def test_yaml_doc(self):
        self._routine( 'data.yaml' )

    def _routine(self, filename):
        raw = self.raw
        uri = os.path.join( self.tempdir, filename )

        api.write( raw, uri )

        data = api.read( uri )
        self.assertDictEqual( raw, data )


class LocalTestCasesYamlDocs( TestCaseLocal ):

    def setUp(self):
        super().setUp()
        self.raw = [ { 'a' : 1, 'b': 2 }, { 'c': 3 } ]

    def test_yaml_docs(self):
        self._routine( 'data.yaml' )

    def _routine(self, filename):
        raw = self.raw
        uri = os.path.join( self.tempdir, filename )

        api.write( raw, uri )

        data = api.read( uri )
        self.assertListEqual( raw, data )


PYTHON_DATA = [1,2,3]

class LocalTestCasePython( unittest.TestCase ):

    def test_python( self ):
        from pyswark.tests.unittests.core import test_io

        mode = "python"
        path = f'{ test_io.__name__}.PYTHON_DATA'
        uri  = f"{ mode }://{ path }"

        Handler = datahandler.get(mode)
        handler = Handler( uri )

        self.assertTrue( handler.exists() )

        data = handler.read()
        self.assertListEqual( PYTHON_DATA, data )

    def test_python_read(self):
        from pyswark.tests.unittests.core import test_io

        uri = f"python://{ test_io.__name__}.PYTHON_DATA"
        data = api.read(uri)
        self.assertListEqual( data, [1,2,3] )

        data.append(4)
        data = api.read(uri)
        self.assertListEqual( data, [1,2,3,4] )

        data = api.read(uri, reloadmodule=True)
        self.assertListEqual( data, [1,2,3] )


class TestReadWriteAcquireCsv( TestCaseLocal ):

    def setUp(self):
        super().setUp()
        self.raw = pandas.DataFrame({'a': [1,2,3]})

    def test_csv(self):
        raw = self.raw
        fn  = "df.csv"
        uri = os.path.join( self.tempdir, fn )

        handler = api.acquire(uri)
        self.assertFalse( handler.exists() )

        api.write(raw, uri)
        self.assertTrue( handler.exists() )

        df = api.read(uri)
        pandas.testing.assert_frame_equal( raw, df )

        handler.rm()
        self.assertFalse( handler.exists() )


class TestReadWriteAcquireHtml( TestCaseLocal ):

    def test_html_url(self):
        url  = 'google.com'
        raw = api.read(url)

        uri = os.path.join( self.tempdir, 'google.html' )
        api.write(raw, uri)
        data = api.read(uri)

        self.assertEqual( raw, data )

    def test_html_file(self):
        raw = '<html> Hello World </html>'
        uri = os.path.join( 'file:/', self.tempdir, 'file.html' )

        api.write(raw, uri)
        data = api.read(uri)

        self.assertEqual( raw, data )


class LocalTestCasesPjson( TestCaseLocal ):

    def setUp(self):
        super().setUp()
        self.raw = MockPjson( i=1, f='2.' )

    def test_pjson(self):
        outpath = f"{ self.tempdir }/y.pjson"
        raw = self.raw
        api.write(raw, outpath)
        data = api.read(outpath)
        self.assertEqual( raw, data )


class MockPjson( base.BaseModel ):
    i: int
    f: float


class TestCustomPyswarkIo( unittest.TestCase ):

    def test_read_from_package(self):
        DF = api.read('pyswark://data/df.csv')
        self.assertIsInstance( DF, pandas.DataFrame )
