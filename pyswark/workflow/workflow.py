from pydantic import field_validator
from pyswark.lib.pydantic import base
from pyswark.workflow.step import Step
from pyswark.workflow.state import State


class Workflow( base.BaseModel ):
    steps: list[ Step ]

    def __init__( self, steps=None ):
        super().__init__( steps=steps or [] )

    @field_validator( 'steps', mode='before' )
    def _steps_before( cls, steps: list[ Step ] ):
        steps = steps if isinstance( steps, list ) else [ steps ]
        return [ cls._step_before( step ) for step in steps ]
        
    @staticmethod
    def _step_before( step: Step ):
        if isinstance( step, dict ):
            step = Step( **step )
        if not isinstance( step, Step ):
            raise ValueError( f"Invalid step: {step}" )
        return step
    
    def addStep( self, step: Step ):
        step = self._step_before( step )
        self.steps.append( step )

    def run( self, state: State ):
        result = None
        for step in self.steps:
            result = step.run( state )
        return result
