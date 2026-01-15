from typing import Any, Union
from pydantic import field_validator
from pyswark.lib.pydantic import base, ser_des
from pyswark.core.models import primitive


class Interface( primitive.Interface ):
   
    def asDict( self ):
        raise NotImplementedError


class Base( Interface ):
    inputs: Any

    def __init__(self, inputs):
        return super().__init__( inputs=inputs )

    @field_validator( 'inputs' )
    def _inputs( cls, inputs ) -> list:
        new = []
        for i, e in enumerate( inputs ):
            element = e

            if isinstance( element, base.BaseModel ):
                element = element.toDict()

            elif isinstance( element, dict ) and ser_des.isSerializedDict( element ):
                element = element

            elif Infer.inScope( element ):
                element = Infer( element ).toDict()

            elif primitive.Infer.inScope( element ):
                element = primitive.Infer( element ).toDict()

            else:
                raise ValueError( f"Cannot handle {type(element)} for data[{i}]" )

            new.append( element )
        return new

    def extractModels(self):
        return [ ser_des.fromDict(e) for e in self.inputs ]

    def extract(self):
        data = []
        for e in self.extractModels():
            model = e
            if isinstance( model, ( Base, primitive.Base )):
                model = model.extract()
            data.append( model )
        return data

    def asCollection( self ):
        return self


class List( Base ):
    inputs: Union[ list, tuple ]

    def asDict(self):
        extracted = self.extract()

        def isRecords(extracted):
            return extracted and all( _isRecord(item) for item in extracted )

        def hasPrimitives(extracted):
            return extracted and any( not _isDictCompatible(item) for item in extracted )

        def _isRecord(item):
            return isinstance(item, dict)

        def _isDictCompatible(item):
            return _isRecord(item) or (isinstance(item, (tuple, list, set)) and len(item) >= 2)


        if isRecords(extracted) or hasPrimitives(extracted):
            """ if all items are records, we need to convert them to a list of records """
            extracted = [(i, item) for i, item in enumerate(extracted)]

        return Dict( extracted )


class Tuple( List ):

    def extract(self):
        return tuple( super().extract() )


class Set( List ):

    def __init__(self, inputs):
        if isinstance( inputs, set ):
            inputs = list( inputs )
        return super().__init__( inputs=inputs )

    def extract(self):
        return set( super().extract() )


class Dict( List ):
    inputs: Union[ dict, list ]

    @field_validator( 'inputs' )
    def _inputs( cls, inputs ) -> list:

        if isinstance( inputs, dict ):
            inputs = list( inputs.items() )
        
        inputs = List( inputs ).extract()

        seen = set()
        for i, e in enumerate( inputs ):

            if isinstance( e, ( list, tuple, set )):
                if len(e) < 2:
                    raise ValueError( f"inputs[{i}] must have a length of 2 or more, got {len(e)} for {e}" )
                k = list(e)[0]
                if k in seen:
                    raise ValueError( f"inputs[{i}] must be unique, got duplicate={k}" )
                seen.add(k)

            elif isinstance( e, dict ):
                for k in e.keys():
                    if k in seen:
                        raise ValueError( f"inputs[{i}] must be unique, got duplicate={k}" )
                    seen.add(k)
            
        return super()._inputs( inputs )

    def extract(self):
        new = []
        keys = set()
        for extracted in super().extract():
            
            data = extracted
            typ  = list
            if isinstance( extracted, dict ):
                data = list( extracted.items() )
            elif isinstance( extracted, ( tuple, list )):
                data = [ extracted ]
                typ  = type( extracted )
            elif isinstance( extracted, set ):
                data = [ tuple(extracted) ]
                typ  = set
            
            for key, *vals in data:
                if key in keys:
                    raise ValueError(f"duplicate keys for {key=}")
                keys.add(key)

                val = vals[0] if len(vals) == 1 else typ(vals)
                new.append(( key, val ))
                
        return dict( new )

    def asDict( self ):
        return self


class Infer( primitive.Infer ):

    TYPE_MAP = {
        list  : List,
        tuple : Tuple,
        set   : Set,
        dict  : Dict,
    }
