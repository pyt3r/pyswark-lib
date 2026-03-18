import unittest
import tempfile
import pathlib
import shutil
from unittest.mock import patch, MagicMock

from pyswark.core.io import api as io_api
from pyswark.sekrets import api, settings
from pyswark.sekrets import hub as sekrets_hub
from pyswark.gluedb import hub as gluedb_hub


def buildDb():
    """Build a sekrets database from string data."""
    sekretsData = """
---
name: woody
sekret: theres_a_snake_in_my_boot
description: Sheriff Woody - You've got a friend in me
---
name: buzz
sekret: to_infinity_and_beyond
description: Space Ranger - Falling with style
"""

    sekrets = io_api.read(sekretsData, 'string')
    sekretsDb = api.Db()
    sekretsDb.postAll(sekrets)
    return sekretsDb


class TestSekrets(unittest.TestCase):
    """Test the sekrets API functionality with toy example data"""

    def setUp(self):
        """Set up test database and settings."""
        # 0. build a sekrets db
        self.sekretsDb = buildDb()

        # 1. create a temp dir
        self.tempdir = tempfile.mkdtemp()

        # 2. write the sekret to the temp dir using file name toy-example.gluedb
        uri = pathlib.Path(self.tempdir) / 'toy-example.gluedb'
        io_api.write( self.sekretsDb, uri )

        # 3. take the full uri and add it to a Settings
        data = {
            'TEST': uri
        }
        self.Settings = settings.Base.createDynamically(data, 'Settings')

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.tempdir)

    def test_hub(self):
        """Test creating a hub and posting the test database."""
        Settings = self.Settings
        hub = gluedb_hub.Hub()
        hub.post(Settings.TEST.uri, name=Settings.TEST.name)
        
        # Verify the hub contains the test database
        self.assertIn(Settings.TEST.name, hub.getNames())
        
        # Extract and verify
        extracted_db = hub.extract(Settings.TEST.name)
        self.assertEqual(set(extracted_db.getNames()), {'woody', 'buzz'})

    def test_build_db(self):
        """Test building a database and posting additional sekrets."""
        sekretsDb = self.sekretsDb

        anotherSekret = """
---
name: mr_potato_head
sekret: im_a_married_spud
description: Mr. Potato Head - Detachable parts, detachable heart
"""

        sekretsDb.post(anotherSekret)
        names = sekretsDb.getNames()
        
        # Assert the names
        self.assertEqual(set(names), {'woody', 'buzz', 'mr_potato_head'})

    def test_extract_sekrets(self):
        """Test extracting sekrets from the database."""
        # Extract woody's sekret
        woody_sekret = self.sekretsDb.acquire('woody')
        self.assertEqual(woody_sekret.sekret, 'theres_a_snake_in_my_boot')
        self.assertEqual(woody_sekret.description, 'Sheriff Woody - You\'ve got a friend in me')

        # Extract buzz's sekret
        buzz_sekret = self.sekretsDb.extract('buzz')
        self.assertDictEqual(buzz_sekret, {'sekret': 'to_infinity_and_beyond', 'description': 'Space Ranger - Falling with style'})


class TestSekretsApi( unittest.TestCase ):
    """Test sekrets.api functions via a mocked hub."""

    def _build_hub(self):
        """Build a base hub (no Settings resolution) with a 'TEST' protocol db."""
        sekretsDb = buildDb()
        h = gluedb_hub.Hub()
        h.post( sekretsDb, name='TEST' )
        return h

    @patch( 'pyswark.sekrets.api.getHub' )
    def test_get_with_protocol(self, mock_getHub):
        """api.get(name, protocol) delegates to hub.extractFromDb."""
        mock_getHub.return_value = self._build_hub()
        result = api.get( 'woody', 'TEST' )
        self.assertIsInstance( result, dict )
        self.assertEqual( result['sekret'], 'theres_a_snake_in_my_boot' )

    @patch( 'pyswark.sekrets.api.getHub' )
    def test_get_without_protocol(self, mock_getHub):
        """api.get(name) without protocol consolidates hub then extracts."""
        mock_getHub.return_value = self._build_hub()
        result = api.get( 'buzz' )
        self.assertIsInstance( result, dict )
        self.assertEqual( result['sekret'], 'to_infinity_and_beyond' )

    @patch( 'pyswark.sekrets.api.getHub' )
    def test_getDb(self, mock_getHub):
        """api.getDb returns the db for a protocol."""
        mock_getHub.return_value = self._build_hub()
        db = api.getDb( 'TEST' )
        self.assertIn( 'woody', db.getNames() )

    def test_Db_returns_empty_sekrets_db(self):
        """api.Db() returns an empty sekrets database."""
        db = api.Db()
        self.assertEqual( db.getNames(), [] )

    def test_sekret_returns_model_class(self):
        """api.sekret('generic') returns the generic Sekret class."""
        from pyswark.sekrets.models.generic import Sekret
        klass = api.sekret( 'generic' )
        self.assertEqual( klass.__name__, Sekret.__name__ )
        self.assertEqual( klass.__module__, Sekret.__module__ )


class TestSekretsDbFallback( unittest.TestCase ):
    """Test _post_fallback paths in sekrets.db.Db."""

    def test_post_dict_with_name_key(self):
        """Posting a dict with 'name' key uses that as record name."""
        db = api.Db()
        db.post( { 'name': 'rex', 'sekret': 'rawr', 'description': 'dinosaur' } )
        self.assertIn( 'rex', db.getNames() )
        extracted = db.extract( 'rex' )
        self.assertEqual( extracted['sekret'], 'rawr' )

    def test_post_dict_without_name_key(self):
        """Posting a dict without 'name' requires explicit name= argument."""
        db = api.Db()
        db.post( { 'sekret': 'sssh', 'description': 'unnamed' }, name='anon' )
        self.assertIn( 'anon', db.getNames() )

    def test_post_multiline_yaml_string_multiple_docs(self):
        """Posting a multi-doc YAML string via read+postAll creates all records."""
        multi = """
---
name: alpha
sekret: a
---
name: beta
sekret: b
"""
        parsed = io_api.read( multi, 'string' )
        db = api.Db()
        db.postAll( parsed )
        self.assertCountEqual( db.getNames(), ['alpha', 'beta'] )
