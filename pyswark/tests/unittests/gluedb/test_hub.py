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


class TestPostToDb( unittest.TestCase ):

    def test_postToDb_persists_to_uri_and_returns_record(self):
        """postToDb adds entry to the db and overwrites the gluedb file at its URI."""
        tempdir = tempfile.mkdtemp()
        try:
            db_1 = buildDB_1()
            db_uri = f'file://{pathlib.Path(tempdir) / "db_1.gluedb" }'
            api.write( db_1, db_uri )
            hub = hub_module.Hub()
            hub.post( db_uri, name='db_1' )
            rec = hub.postToDb(
                collection.Dict( {'persisted': 42} ),
                'db_1',
                name='persisted_entry',
            )
            self.assertIsNotNone( rec )
            db_read_back = api.read( db_uri )
            self.assertIn( 'persisted_entry', db_read_back.getNames() )
            self.assertDictEqual(
                db_read_back.extract( 'persisted_entry' ),
                {'persisted': 42},
            )
        finally:
            shutil.rmtree( tempdir )

    def test_postToDb_requires_name_when_not_on_obj(self):
        """postToDb raises ValueError when name is required but missing."""
        hub = buildHub()
        with self.assertRaises( ValueError ) as ctx:
            hub.postToDb( collection.Dict( {'x': 1} ), 'db_1' )
        self.assertIn( 'name', str( ctx.exception ).lower() )


class TestDbHelpers( unittest.TestCase ):

    def setUp(self):
        self.hub = buildHub()

    def test_get_extract_acquire_from_db_inline(self):
        """getFromDb / extractFromDb / acquireFromDb delegate to underlying GlueDb."""
        hub = self.hub
        db_1 = hub.extract( 'db_1' )

        rec_direct = db_1.get( 'a' )
        rec_via_hub = hub.getFromDb( 'db_1', 'a' )
        self.assertEqual( rec_direct.info.name, rec_via_hub.info.name )

        extracted_direct = db_1.extract( 'a' )
        extracted_via_hub = hub.extractFromDb( 'db_1', 'a' )
        self.assertEqual( extracted_direct, extracted_via_hub )

        acq_direct = db_1.acquire( 'a' )
        acq_via_hub = hub.acquireFromDb( 'db_1', 'a' )
        self.assertEqual( type( acq_direct ), type( acq_via_hub ) )

    def test_putToDb_and_deleteFromDb_persist_to_uri(self):
        """putToDb and deleteFromDb modify the URI-backed GlueDb and persist changes."""
        tempdir = tempfile.mkdtemp()
        try:
            db_1 = buildDB_1()
            db_uri = f'file://{pathlib.Path(tempdir) / "db_1.gluedb" }'
            api.write( db_1, db_uri )

            hub = hub_module.Hub()
            hub.post( db_uri, name='db_1' )

            # putToDb updates existing record 'a'
            hub.putToDb(
                collection.Dict( {'a': 100} ),
                'db_1',
                name='a',
            )
            db_after_put = api.read( db_uri )
            self.assertDictEqual( db_after_put.extract( 'a' ), {'a': 100} )

            # deleteFromDb removes record 'b'
            success = hub.deleteFromDb( 'db_1', 'b' )
            self.assertTrue( success )
            db_after_delete = api.read( db_uri )
            self.assertNotIn( 'b', db_after_delete.getNames() )
        finally:
            shutil.rmtree( tempdir )

    def test_mergeToDb_persist_to_uri(self):
        """mergeToDb merges another GlueDb into the target and persists to its URI."""
        tempdir = tempfile.mkdtemp()
        try:
            db_target = buildDB_1()
            db_other = buildDB_2()
            db_uri = f'file://{pathlib.Path( tempdir ) / "db_merged.gluedb" }'
            api.write( db_target, db_uri )

            hub = hub_module.Hub()
            hub.post( db_uri, name='db_main' )

            hub.mergeToDb( db_other, 'db_main' )

            db_after_merge = api.read( db_uri )
            self.assertCountEqual(
                db_after_merge.getNames(),
                ['a', 'b', 'c', 'd'],
            )
        finally:
            shutil.rmtree( tempdir )
