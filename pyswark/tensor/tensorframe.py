from pyswark.tensor import tensordict


class _Mixin:

    def __len__(self):
        if self._length:
            return self._length
        raise ValueError("length not yet set")

    @property
    def _length(self):
        keys = list( self.keys() )
        if keys:
            return len( self[ keys[0] ])

    @classmethod
    def _parseSelf( cls, data ):
        if isinstance( data, cls ):
            return ( True, data.data )

    @staticmethod
    def _setItemValidate( data, key, val, length ):
        if key in data:
            raise ValueError( f"cannot overwrite { key= }" )

        if length is not None and length != len( val ):
            raise ValueError( f"All array lengths must match: len({ key })={ len( val ) } != { length }")

    def getRecord( self, index ):
        return { k: self[ k ][ index ] for k in self.keys() }

    def merge( self, other ):
        klass  = self.__class__
        new    = klass()
        frames = [ self, klass( other ) ]
        for f in frames:
            for k, v in f.items():
                new[k] = v
        return new


class TensorFrame( _Mixin, tensordict.TensorDict ):
    """ a tensorDict that ensures the lengths of all items are the same """


class VectorFrame( _Mixin, tensordict.VectorDict ):
    """ a vectorDict that ensures the lengths of all items are the same """


class MatrixFrame( _Mixin, tensordict.MatrixDict ):
    """ a matrixDict that ensures the lengths of all items are the same """
