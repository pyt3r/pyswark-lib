from typing import Union, Any
from pyswark.query import interface

import pandas
import numpy


class Equals( interface.Equals ):
    
    def __call__(self, value, records=None):
        return value == self.inputs


class OneOf( interface.OneOf ):

    def __call__(self, value, records=None):
        return value.isin( self.inputs )


class Query( interface.Query ):
    """ query for a native list of dicts (or recoords )"""
    
    def all( self, records: pandas.DataFrame, params ):
        """ records must meet all param criteria """
        indices = pandas.Series( numpy.ones( len(records), dtype=bool ))
        for key, condition in params:
            indices &= condition( records[ key ], records )
        return indices

    def any( self, records: pandas.DataFrame, params ):
        """ records must meet any param criteria """
        indices = pandas.Series( numpy.ones( len(records), dtype=bool ))
        for key, condition in params:
            indices |= condition( records[ key ], records )
        return indices
    
    @classmethod
    def collectResults( cls, records, indices, collect ):
        columns = collect if collect else records.columns
        return records.loc[ indices, columns ]
