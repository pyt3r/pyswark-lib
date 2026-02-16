import unittest
import tempfile
import pathlib
import shutil

from pyswark.lib.pydantic import ser_des

from pyswark.core.models import collection
from pyswark.core.io import api

from pyswark.gluedb import db as db_module
from pyswark.gluedb import hub as hub_module


def buildDB_1():
    """Build DB_1 with records 'a' and 'b' containing test dictionaries."""
    db = db_module.Db()
    db.post(collection.Dict({'a': 1}), name='a')
    db.post(collection.Dict({'b': 2, 'c': 3}), name='b')
    return db


def buildDB_2():
    """Build DB_2 with records 'c' and 'd' containing test dictionaries."""
    db = db_module.Db()
    db.post(collection.Dict({'d': 4, 'e': 5, 'f': 6}), name='c')
    db.post(collection.Dict({'g': 7, 'h': 8, 'i': 9}), name='d')
    return db


def buildHub():
    """Build a hub with db_1 and db_2."""
    hub = hub_module.Hub()
    hub.post(buildDB_1(), name='db_1')
    hub.post(buildDB_2(), name='db_2')
    return hub


class HubTestCases( unittest.TestCase ):

    def setUp(self):
        """Set up test hub in temp file."""
        self.tempdir = tempfile.mkdtemp()
        
        # Create hub and save to file
        hub = buildHub()
        self.hub_path = pathlib.Path(self.tempdir) / 'hub.gluedb'
        api.write(hub, f'file://{self.hub_path}')

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.tempdir)

    def test_load_contents_from_a_hub(self):
        hub = api.read(f'file://{self.hub_path}')

        db = hub.extract('db_2')
        c  = db.extract( "c" )
        self.assertDictEqual( c, {'d': 4, 'e': 5, 'f': 6} )

    def test_consolidating_a_hub_to_a_db(self):
        hub = api.read(f'file://{self.hub_path}')

        db = hub.toDb()
        expected = ['a', 'b', 'c', 'd']
        test = db.getNames()

        self.assertListEqual(expected, test)

    def test_ser_des(self):
        hub = api.read(f'file://{self.hub_path}')

        ser = hub.toJson()
        des = ser_des.fromJson( ser )

        self.assertListEqual( hub.getNames(), des.getNames() )


class TestCRUD( unittest.TestCase ):

    def setUp(self):
        """Set up test hub."""
        self.hub = buildHub()

    def test_POST_content_in_a_hub(self):
        hub = hub_module.Hub()
        hub.merge( self.hub )

        record = hub.get("db_2")
        hub.post( name='db_2.copy', obj=record.body)

        db_orig = hub.extract('db_2')
        db_copy = hub.extract('db_2.copy')

        self.assertListEqual( hub.getNames(), ['db_1', 'db_2', 'db_2.copy'] )
        self.assertDictEqual( db_orig.toDict(), db_copy.toDict() )

    def test_PUT_content_in_a_hub(self):
        hub = buildHub()

        old = hub.extract( 'db_2' )

        hub.put( name='db_2', obj=hub.get("db_1").body )
        new = hub.extract('db_2')

        self.assertListEqual( old.getNames(), ['c', 'd'] )
        self.assertListEqual( new.getNames(), ['a', 'b'] )
