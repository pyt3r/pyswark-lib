import unittest
import tempfile
import pathlib
import shutil

from pyswark.core.io import api as io_api
from pyswark.sekrets import api, settings, db
from pyswark.gluedb import api as gluedb_api


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
    sekretsDb = db.Db()
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
        hub = gluedb_api.newHub()
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
