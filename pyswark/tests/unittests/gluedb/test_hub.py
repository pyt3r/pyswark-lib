import unittest

from pyswark.lib.pydantic import ser_des

from pyswark.gluedb import api
from pyswark.examples.gluedb.settings import Settings


class HubTestCases( unittest.TestCase ):

    def test_load_contents_from_a_hub(self):
        uri = f'{ Settings.HUB.uri }.HUB'
        hub = api.load(uri)

        db = hub.load('db_2')
        c  = db.load( "c" )
        self.assertDictEqual( c, {'d': 4, 'e': 5, 'f': 6} )

    def test_consolidating_a_hub_to_a_db(self):
        uri = f'{ Settings.HUB.uri }.HUB'
        hub = api.load(uri)

        db = hub.toDb()
        expected = ['a', 'b', 'c', 'd']
        test = db.getNames()

        self.assertListEqual(expected, test)

    def test_ser_des(self):
        uri = f'{ Settings.HUB.uri }.HUB'
        hub = api.load(uri)

        ser = hub.toJson()
        des = ser_des.fromJson( ser )

        self.assertListEqual( hub.getNames(), des.getNames() )


class TestCRUD( unittest.TestCase ):

    def test_POST_content_in_a_hub(self):

        uri = f'{ Settings.HUB.uri }.HUB'
        old = api.load(uri)

        hub = api.newHub()
        hub.merge( old )

        record = hub.get("db_2")
        hub.post('db_2.copy', record.body)

        db_orig = hub.load('db_2')
        db_copy = hub.load('db_2.copy')

        self.assertListEqual( hub.getNames(), ['db_1', 'db_2', 'db_2.copy'] )
        self.assertDictEqual( db_orig.toDict(), db_copy.toDict() )

    def _test_PUT_content_in_a_hub(self):

        uri = f'{ Settings.HUB.uri }.HUB'
        hub = api.load(uri)


    def test_DELETE_content_in_a_hub(self):
        pass

