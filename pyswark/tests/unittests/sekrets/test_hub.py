import unittest

from pyswark.sekrets import hub as sekrets_hub
from pyswark.sekrets import db as sekrets_db
from pyswark.sekrets.settings import Settings
from pyswark.sekrets.models import generic as generic_model


def build_sekrets_db():
    """Build a simple sekrets Db with one record."""
    db = sekrets_db.Db()
    db.post(
        generic_model.Sekret(sekret="top-secret", description="test"),
        name="alice",
    )
    return db


class TestSekretsHubNameResolution(unittest.TestCase):

    def setUp(self):
        self.hub = sekrets_hub.Hub()
        self.db = build_sekrets_db()
        # Use canonical Settings name (e.g. 'GDRIVE2') as stored key
        self.setting = Settings.GDRIVE2
        self.canonical_name = self.setting.name
        self.alias = "gdrive2"  # Alias resolved via Settings.get(...)
        self.hub.post(self.db, name=self.canonical_name)

    def test_extract_resolves_alias_positional(self):
        """extract(dbName) should resolve aliases via Settings before delegating."""
        extracted_alias = self.hub.extract(self.alias)
        extracted_canonical = self.hub.extract(self.canonical_name)
        self.assertEqual(extracted_alias.getNames(), extracted_canonical.getNames())
        self.assertEqual(
            extracted_alias.extract("alice"),
            extracted_canonical.extract("alice"),
        )

    def test_extract_resolves_alias_keyword(self):
        """extract(name=...) should also resolve aliases via Settings."""
        extracted_alias = self.hub.extract(name=self.alias)
        extracted_canonical = self.hub.extract(self.canonical_name)
        self.assertEqual(extracted_alias.getNames(), extracted_canonical.getNames())
        self.assertEqual(
            extracted_alias.extract("alice"),
            extracted_canonical.extract("alice"),
        )

    def test_get_extract_acquire_from_db_use_resolved_name(self):
        """getFromDb / extractFromDb / acquireFromDb all resolve dbName via Settings."""
        # Direct calls on the same hub using canonical name
        rec_direct = self.hub.getFromDb(self.canonical_name, "alice")
        extracted_direct = self.hub.extractFromDb(self.canonical_name, "alice")
        acq_direct = self.hub.acquireFromDb(self.canonical_name, "alice")

        rec_via_alias = self.hub.getFromDb(self.alias, "alice")
        self.assertEqual(rec_via_alias.info.name, rec_direct.info.name)
        self.assertEqual(rec_via_alias.body.model, rec_direct.body.model)
        self.assertEqual(rec_via_alias.body.contents, rec_direct.body.contents)

        extracted_via_alias = self.hub.extractFromDb(self.alias, "alice")
        self.assertEqual(extracted_via_alias, extracted_direct)

        acq_via_alias = self.hub.acquireFromDb(self.alias, "alice")
        self.assertEqual(type(acq_via_alias), type(acq_direct))

    def test_delete_from_db_resolves_name_and_deletes(self):
        """deleteFromDb should resolve dbName alias and delete the record."""
        success = self.hub.deleteFromDb(self.alias, "alice", overwrite=False)
        self.assertTrue(success)

