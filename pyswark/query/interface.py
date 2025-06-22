from typing import Union, Any
from pydantic import field_validator, Field
from pyswark.lib.pydantic import base, ser_des


class Param( base.BaseModel ):
    inputs: Any


class Query( base.BaseModel ):
    params: Union[ 
        dict[ str, Union[ Param, dict ]], 
        list[ tuple[ str, Union[ Param, dict ] ]],
    ]
    collect: Union[ str, list[str], tuple[str] ] = Field( default_factory=lambda: [] )

    def __init__(self, params=None, collect=None, **otherParams ):
        params  = [] if params is None else params
        params  = list( params.items() ) if isinstance( params, dict ) else params
        params  = [ params ] if isinstance( params, tuple ) else params
        params += list( otherParams.items() ) 
        super().__init__( params=params, collect=collect or [] )
    
    @field_validator( 'params', mode='after' )
    def _params_after(cls, params):
        return [( k, p if isinstance(p, dict) else p.toDict() ) for k, p in params ]

    @field_validator( 'collect', mode='after' )
    def _collect_after(cls, collect):
        if not isinstance( collect, (list, tuple) ):
            collect = [ collect ]
        return collect

    def _extractParams(self):
        return [( k, ser_des.fromDict( p )) for k, p in self.params ]

    def runAll( self, records: list[ dict ] ):
        return self.all( records, self._extractParams() )

    def runAny( self, records: list[ dict ] ):
        return self.any( records, self._extractParams() )

    def all( self, records: list[ dict ], params ):
        """ records must meet all param criteria """
        results = []
        for record in records:
            match = True
            for key, condition in params:
                if not self.runCondition( record, key, condition ):
                    match = False
                    break
            if match:
                results.append(record)

        return self.collectResults( results )

    def any( self, records: list[ dict ], params ):
        """ records must meet any param criteria """
        results = []
        for record in records:
            match = False
            for key, condition in params:
                if self.runCondition( record, key, condition ):
                    match = True
                    break
            if match:
                results.append(record)

        return self.collectResults( results )

    @classmethod
    def runCondition( cls, record, key, condition ):
        val = cls.getVal( record, key, condition )
        return condition( val )

    @staticmethod
    def getVal( record, key, condition=None ):
        raise NotImplementedError

    def collectResults( self, results ):
        if self.collect:
            results = [{ c: self.getVal(r, c) for c in self.collect } for r in results ]
        return results
