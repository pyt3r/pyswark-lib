from typing import Union, Any
from pyswark.query import interface


class Equals( interface.Equals ):
    
    def __call__(self, value, records=None):
        return value == self.inputs


class OneOf( interface.OneOf ):

    def __call__(self, value, records=None):
        return value in self.inputs


class Query( interface.Query ):
    """ query for a native list of dicts (or recoords )"""
    
    def all( self, records: list[ dict ], params ):
        """ records must meet all param criteria """
        results = []
        for record in records:
            match = True
            for key, condition in params:
                if not self.runCondition( key, condition, record, records ):
                    match = False
                    break
            if match:
                results.append(record)

        return results

    def any( self, records: list[ dict ], params ):
        """ records must meet any param criteria """
        results = []
        for record in records:
            match = False
            for key, condition in params:
                if self.runCondition( key, condition, record, records ):
                    match = True
                    break
            if match:
                results.append(record)

        return results
    
    @classmethod
    def runCondition( cls, key, condition, record, records=None ):
        val = cls.getVal( record, key, condition )
        return condition( val, records )

    @staticmethod
    def getVal( record, key, condition=None ):
        return record.get( key )

    def collectResults( self, results ):
        if self.collect:
            results = [{ c: self.getVal(r, c) for c in self.collect } for r in results ]
        return results
