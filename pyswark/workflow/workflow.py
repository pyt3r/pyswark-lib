#%%
import logging
from pydantic import field_validator, Field
from pyswark.lib.pydantic import base
from pyswark.workflow.step import Step
from pyswark.workflow.state import State

logger = logging.getLogger(__name__)


class Extracts( base.BaseModel ):
    """ extracted model inputs or outputs """
    
    data: dict[int, dict] = Field( default_factory=dict )

    def __contains__( self, i ):
        return i in self.data

    def get( self, i ):
        return self.data[i]

    def add( self, i, extract ):
        self.data[i] = extract

    def equal( self, i: int, other ):
        return self.data[i] == other


class Workflow( base.BaseModel ):
    """ workflow of steps to be run """
    
    steps : list[ Step ]

    inputs  : Extracts = Field( default_factory=Extracts )
    outputs : Extracts = Field( default_factory=Extracts )

    useExtract      : bool = True
    populateExtract : bool = True

    stepsSkipped : list[ int ] = Field( default_factory=list )
    stepsRan     : list[ int ] = Field( default_factory=list )

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

    @field_validator( 'inputs','outputs', mode='before' )
    def _extracts_before( cls, extracts: Extracts ):

        if isinstance( extracts, dict ):
            extracts = extracts if 'data' in extracts else { 'data': extracts }
            extracts = Extracts( **extracts )

        return extracts

    def addStep( self, step: Step ):
        step = self._step_before( step )
        self.steps.append( step )

    def run( self, state: State ):

        stateOutput = None
        for i, step in enumerate( self.steps ):
            state, stateOutput = self._runStep( i, step, state )

        return stateOutput

    def _runStep( self, i: int, step: Step, state: State ):
        stateInput  = step.extractStateInputFromState( state )
        modelInput  = step.extractModelInputFromStateInput( stateInput )

        skip, modelOutput = self._skipModel( i, modelInput )

        stepinfo = f"Step{i:>3}. {step.model}"
        if skip:
            self.stepsSkipped.append( i )
            logger.info( f"Skipped {stepinfo}." )

        else:
            logger.info( f"Running {stepinfo}..." )
            model       = step.extractModelFromModelInput( modelInput )
            modelOutput = model.run()
            self.stepsRan.append( i )
            logger.info( f"done." )

        self._extractOutput( i, modelOutput )

        stateOutput = step.extractStateOutputFromModelOutput( modelOutput )
        step.loadStateOutputToState( state, stateOutput )
        return state, stateOutput

    def _skipModel( self, i: int, modelInput ):
        skip        = False
        modelOutput = None

        if all(( self.useExtract, i in self.inputs, i in self.outputs )):
            if self.inputs.equal( i, modelInput ):
                skip        = True
                modelOutput = self.outputs.get( i )

        if self.populateExtract:
            self.inputs.add( i, modelInput )

        return skip, modelOutput

    def _extractOutput( self, i: int, modelOutput ):
        if self.populateExtract:
            self.outputs.add( i, modelOutput )

    def getModelInput( self, i: int ):
        return self.inputs.get( i )

    def getModelOutput( self, i: int ):
        return self.outputs.get( i )

    def getModel( self, i: int ):
        step = self.steps[i]
        modelInput = self.getModelInput(i)
        return step.extractModelFromModelInput( modelInput )
