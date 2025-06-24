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
        indices = []
        for i, record in enumerate(records):
            match = True
            for key, condition in params:
                if not self.runCondition( key, condition, record, records ):
                    match = False
                    break
            if match:
                indices.append(i)

        return indices

    def any( self, records: list[ dict ], params ):
        """ records must meet any param criteria """
        indices = []
        for i, record in enumerate(records):
            match = False
            for key, condition in params:
                if self.runCondition( key, condition, record, records ):
                    match = True
                    break
            if match:
                indices.append(i)

        return indices
    
    @classmethod
    def runCondition( cls, key, condition, record, records ):
        val = cls.getVal( record, key )
        return condition( val, records )

    @staticmethod
    def getVal( record, key ):
        return record.get( key )

    @classmethod
    def collectResults( cls, records, indices, collect ):
        results = super().collectResults( records, indices, collect )
        if collect:
            results = [{ c: cls.getVal(r, c) for c in collect } for r in results ]
        return results
