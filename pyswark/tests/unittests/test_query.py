import unittest
from pyswark.query.native import Query, OneOf, Equals
from pyswark.lib.pydantic import ser_des


class NativeTestCase( unittest.TestCase ):

    def setUp(self):
        self.records = [
            {'name': 'Aaron Judge', 'team': 'yankees', 'position': 'OF'},
            {'name': 'Pete Alonso', 'team': 'mets', 'position': '1B'},
            {'name': 'Mookie Betts', 'team': 'dodgers', 'position': 'OF'},
            {'name': 'Francisco Lindor', 'team': 'mets', 'position': 'SS'},
        ]

    def test_query_all_using_params(self):
        records = self.records
        query   = Query(params={'team' : OneOf(['mets', 'yankees']) })
        results = query.runAll( records )
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge', 'Pete Alonso', 'Francisco Lindor'] )
    
    def test_query_any_using_kw(self):
        records = self.records
        query   = Query( params=[ ('team', Equals('mets')), ('team', Equals('yankees')) ])
        results = query.runAny( records )
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge', 'Pete Alonso', 'Francisco Lindor'] )

    def test_query_all_using_kw(self):
        records = self.records
        query   = Query( team=OneOf(['mets', 'yankees']) )
        results = query.runAll( records )
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge', 'Pete Alonso', 'Francisco Lindor'] )

    def test_query_all_using_params_and_kw(self):
        records = self.records
        query   = Query( params={'team' : OneOf(['mets', 'yankees'])}, position=Equals('OF'))
        results = query.runAll( records )
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge'] )
        
    def test_collect(self):
        records = self.records
        query   = Query( team=OneOf(['mets', 'yankees']), position=Equals('OF'), collect='name' )
        results = query.runAll( records )
        self.assertListEqual( results, [{'name': 'Aaron Judge'}] )

    def test_ser_des(self):
        query = Query( team=OneOf(['mets', 'yankees']), position=Equals('OF'), collect=['name', 'position'] ) 
        ser = query.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( query, des )
