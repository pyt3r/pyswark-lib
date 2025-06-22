#%%
from typing import Union, Any
from pyswark.query import interface


class Equals( interface.Param ):
    """ value == other """
    inputs: Union[ str, int, float ]

    def __init__(self, inputs):
        super().__init__(inputs=inputs)

    def __call__(self, value):
        return value == self.inputs


class OneOf( interface.Param ):
    """ value in [ *values ] """
    inputs: list

    def __init__(self, inputs):
        super().__init__(inputs=inputs)

    def __call__(self, value):
        return value in self.inputs


class Query( interface.Query ):
    """ query for a native list of dicts (or recoords )"""
    
    @staticmethod
    def getVal( record, key, condition=None ):
        return record.get( key )
