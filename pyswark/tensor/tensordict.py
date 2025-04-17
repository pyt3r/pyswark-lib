from typing import Dict, ClassVar
from pydantic import field_validator, Field

from pyswark.lib.pydantic import base
from pyswark.tensor import tensor

_VALS = {
    'tensor': tensor.Tensor,
    'vector': tensor.Vector,
    'matrix': tensor.Matrix,
}
_KEYS = {
    k: str for k in _VALS.keys() }

_DICTS = {
    k: Dict[ _KEYS[k], _VALS[k] ] for k in _VALS.keys() }

_FIELDS = {
    k: Field( default_factory=lambda : {}, description=f'data for {k}' ) for k in _VALS.keys() }

def _make_getattr( k ):
    def _getattr( model ):
        return getattr( model, k )
    return _getattr

_GETATTRS = {
    k: _make_getattr( k ) for k in _VALS.keys() }


class TensorDict( base.BaseModel ):
    _KEY : ClassVar = 'tensor'
    data : _DICTS[ _KEY] = _FIELDS[ _KEY]

    def __init__( self, data=None ):
        return super().__init__( data=data or {} )

    def __getitem__(self, item):
        f = _GETATTRS[ self._KEY]
        return f( self.data[ item ] )

    def __setitem__(self, key, val):
        self.data, *_ = self._setItem( self.data, key, val, self._length )

    def __len__(self):
        return len( self.data )

    def items(self):
        return zip( self.keys(), self.values() )

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    @field_validator( 'data', mode='before' )
    def _parseData(cls, data):

        parsable = cls._parseSelf( data )
        parsable, parsed = ( False, None ) if ( parsable is None ) else parsable

        if parsable:
            return parsed

        if isinstance( data, TensorDict ):
            return data.data

        if not isinstance( data, dict ):
            raise TypeError( f"{ type(data)= } must be dict" )

        return cls._setData( data )

    @staticmethod
    def _parseSelf( data ):
        return ( False, None )

    @classmethod
    def _setData( cls, old ):
        new = {}
        length = None
        for k, v in old.items():
            new, kk, vv = cls._setItem( new, k, v, length )
            length = len( vv )
        return new

    @classmethod
    def _setItem( cls, data, key, val, length=None ):
        Key = _KEYS[ cls._KEY]
        Val = _VALS[ cls._KEY]

        key = key if isinstance( key, Key ) else Key( key )
        val = val if isinstance( val, Val ) else Val( val )

        cls._setItemValidate( data, key, val, length )

        data[ key ] = val
        return ( data, key, val )

    @staticmethod
    def _setItemValidate( data, key, val, length ):
        """ abstract method for setItem validation """

    @property
    def _length(self):
        """ abstract method for length """


class VectorDict( TensorDict ):
    _KEY : ClassVar = 'vector'
    data : _DICTS[ _KEY] = _FIELDS[ _KEY]


class MatrixDict( TensorDict ):
    _KEY : ClassVar = 'matrix'
    data : _DICTS[ _KEY] = _FIELDS[ _KEY]
