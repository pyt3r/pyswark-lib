from typing import Union, Any
from pydantic import field_validator, Field
from pyswark.lib.pydantic import base, ser_des


class Param( base.BaseModel ):
    inputs: Any

    def __init__(self, inputs):
        super().__init__(inputs=inputs)
        
    def __call__( self, value, records=None ):
        """ main call """


class Equals( Param ):
    """ value == other """
    inputs: Union[ bool, str, int, float ]


class OneOf( Param ):
    """ value in [ *values ] """
    inputs: list


class Query( base.BaseModel ):
    params: Union[ 
        dict[ str, Union[ Param, dict ]], 
        list[ tuple[ str, Union[ Param, dict ] ]],
    ]
    collect: Union[ str, list[str], tuple[str] ] = Field( default_factory=lambda: [] )

    def __init__(self, params=None, collect=None, **otherParams ):
        params = self._params_to_list( params, otherParams )
        super().__init__( params=params , collect=collect or [] )
    
    @staticmethod
    def _params_to_list( params, otherParams ):
        params = [] if params is None else params
        params = list( params.items() ) if isinstance( params, dict ) else params
        params = [ params ] if isinstance( params, tuple ) else params
        params = [ params ] if not isinstance( params, list ) else params
        return params + list( otherParams.items() ) 

    @field_validator( 'params', mode='before' )
    def _params_before(cls, params):
        return cls._extract( params )

    @field_validator( 'params', mode='after' )
    def _params_after(cls, params):
        return cls._load( params )

    @field_validator( 'collect', mode='after' )
    def _collect_after(cls, collect):
        if not isinstance( collect, (list, tuple) ):
            collect = [ collect ]
        return collect

    @staticmethod
    def _load( params ):
        return [( k, p if isinstance(p, dict) else p.toDict() ) for k, p in params ]

    @staticmethod
    def _extract( params ):
        return [( k, ser_des.fromDict( p ) if isinstance(p, dict) else p) for k, p in params ]

    def _extractParams(self):
        return self._extract( self.params )

    def runAll( self, records: list[ Any ] ):
        records = self.extractRecords( records )
        indices = self.all( records, self._extractParams() )
        return self.collectResults( records, indices, self.collect )

    def runAny( self, records: list[ Any ] ):
        records = self.extractRecords( records )
        indices = self.any( records, self._extractParams() )
        return self.collectResults( records, indices, self.collect )

    @classmethod
    def extractRecords( cls, records: list[ Any ]):
        """ optional extraction step, say to convert to a list of dicts """
        return records

    def all( self, records: list[ dict ], params ):
        """ records must meet all param criteria """
        raise NotImplementedError

    def any( self, records: list[ dict ], params ):
        """ records must meet any param criteria """
        raise NotImplementedError

    @classmethod
    def collectResults( cls, records, indices, collect ):
        return [ records[i] for i in indices ]
