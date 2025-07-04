import pandas
from pyswark.query import interface, native, dataframe


class _Param:
     
    def __call__(self, value, records):
        kwargs = self._getKwargs()
        klass  = self._getKlass( records )
        param  = klass( **kwargs )
        return param( value )

    def _getKwargs( self ):
        return { 'inputs' : self.inputs }


class Equals( _Param, interface.Equals ):

    @staticmethod
    def _getKlass( records ):
        if isinstance( records, list ):
            return native.Equals
        if isinstance( records, pandas.DataFrame ):
            return dataframe.Equals

class OneOf( _Param, interface.OneOf ):

    @staticmethod
    def _getKlass( records ):
        if isinstance( records, list ):
            return native.OneOf
        if isinstance( records, pandas.DataFrame ):
            return dataframe.OneOf


class _Query:
    """ query for a native list of dicts (or recoords )"""
    
    def __call__( self, records ):
        kwargs = self._getKwargs()
        klass  = self._getKlass( records )
        query  = klass( **kwargs )
        return self._call( query, records )
    
    def _getKwargs( self ):
        return { 'params' : self.params, 'collect' : self.collect }

    @staticmethod
    def _getKlass( records ):
        if isinstance( records, list ):
            return native.Query
        if isinstance( records, pandas.DataFrame ):
            return dataframe.Query


    @staticmethod
    def _call( query, records ):
        return query.runAll( records )


class QueryAll( _Query, interface.Query ):

    @staticmethod
    def _call( query, records ):
        return query.runAll( records )


class QueryAny( _Query, interface.Query  ):

    @staticmethod
    def _call( query, records ):
        return query.runAny( records )