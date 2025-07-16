import unittest
import pandas

from pyswark.query.model import QueryAll, QueryAny, OneOf, Equals
from pyswark.lib.pydantic import ser_des


class Mixin:
    def setUp(self):
        self.records = [
            {'name': 'Aaron Judge', 'team': 'yankees', 'position': 'OF'},
            {'name': 'Pete Alonso', 'team': 'mets', 'position': '1B'},
            {'name': 'Mookie Betts', 'team': 'dodgers', 'position': 'OF'},
            {'name': 'Francisco Lindor', 'team': 'mets', 'position': 'SS'},
        ]

    def test_query_all_using_params(self):
        records = self.records
        query   = QueryAll(params={'team' : OneOf(['mets', 'yankees']) })
        return query( records )
    
    def test_query_any_using_kw(self):
        records = self.records
        query   = QueryAny( params=[ ('team', Equals('mets')), ('team', Equals('yankees')) ])
        return query( records )

    def test_query_all_using_kw(self):
        records = self.records
        query   = QueryAll( team=OneOf(['mets', 'yankees']) )
        return query( records )

    def test_query_all_using_params_and_kw(self):
        records = self.records
        query   = QueryAll( params={'team' : OneOf(['mets', 'yankees'])}, position=Equals('OF'))
        return query( records )

    def test_collect(self):
        records = self.records
        query   = QueryAll( team=OneOf(['mets', 'yankees']), position=Equals('OF'), collect='name' )
        return query( records )

    def test_ser_des(self):
        query = QueryAll( team=OneOf(['mets', 'yankees']), position=Equals('OF'), collect=['name', 'position'] ) 
        ser = query.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( query, des )


class NativeTestCase( Mixin, unittest.TestCase ):

    def setUp(self):
        super().setUp()

    def test_query_all_using_params(self):
        results = super().test_query_all_using_params()
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge', 'Pete Alonso', 'Francisco Lindor'] )
    
    def test_query_any_using_kw(self):
        results = super().test_query_any_using_kw()
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge', 'Pete Alonso', 'Francisco Lindor'] )

    def test_query_all_using_kw(self):
        results = super().test_query_all_using_kw()
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge', 'Pete Alonso', 'Francisco Lindor'] )

    def test_query_all_using_params_and_kw(self):
        results = super().test_query_all_using_params_and_kw()
        results = [ r['name'] for r in results ]
        self.assertListEqual( results, ['Aaron Judge'] )
        
    def test_collect(self):
        results = super().test_collect()
        self.assertListEqual( results, [{'name': 'Aaron Judge'}] )



class DataFrameTestCase( Mixin, unittest.TestCase ):

    def setUp(self):
        super().setUp()
        self.records = pandas.DataFrame( self.records )
