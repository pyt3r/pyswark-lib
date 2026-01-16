"""
Workflow Orchestration
======================

This module provides the Workflow class for orchestrating multi-step
computations with caching and reproducibility. Workflows manage state
between steps and can skip steps when inputs haven't changed.

Key Concepts
------------
- **Workflow**: A sequence of Steps with input/output caching
- **Step**: A single unit of work with defined inputs and outputs
- **State**: Shared data store that persists between steps

Example
-------
>>> from pyswark.workflow.workflow import Workflow
>>> from pyswark.workflow.step import Step
>>> from pyswark.workflow.state import State
>>>
>>> workflow = Workflow(steps=[
...     Step(model='mymodule.PreprocessModel',
...          inputs={'raw_data': 'data'},
...          outputs={'processed': 'clean_data'}),
...     Step(model='mymodule.AnalysisModel',
...          inputs={'clean_data': 'data'},
...          outputs={'result': 'analysis'})
... ])
>>>
>>> state = State()
>>> state.post(raw_dataframe, name='data')
>>> result = workflow.run(state)
"""

import logging
from pydantic import field_validator, Field
from pyswark.lib.pydantic import base
from pyswark.workflow.step import Step
from pyswark.workflow.state import State

logger = logging.getLogger(__name__)


class Extracts( base.BaseModel ):
    """
    Container for cached model inputs or outputs.

    Used internally by Workflow to store and compare inputs/outputs
    for skip logic.
    """
    
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
    """
    Orchestrates a sequence of computational steps with caching.

    A Workflow manages the execution of multiple Steps, passing data
    between them via a shared State object. It supports caching of
    inputs/outputs to skip steps when inputs haven't changed.

    Parameters
    ----------
    steps : list[Step]
        The sequence of steps to execute.
    useExtracts : bool, default=True
        Whether to use cached inputs/outputs for skip logic.
    populateExtracts : bool, default=True
        Whether to store inputs/outputs for future runs.

    Attributes
    ----------
    stepsSkipped : list[int]
        Indices of steps that were skipped (cached).
    stepsRan : list[int]
        Indices of steps that were executed.

    Example
    -------
    >>> workflow = Workflow(steps=[step1, step2, step3])
    >>> state = State()
    >>> state.post('input_data', my_data)
    >>> result = workflow.run(state)
    """
    
    steps : list[ Step ]

    modelInputs  : Extracts = Field( default_factory=Extracts )
    modelOutputs : Extracts = Field( default_factory=Extracts )

    useExtracts      : bool = True
    populateExtracts : bool = True

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

    @field_validator( 'modelInputs', 'modelOutputs', mode='before' )
    def _extracts_before( cls, extracts: Extracts ):

        if isinstance( extracts, dict ):
            extracts = extracts if 'data' in extracts else { 'data': extracts }
            extracts = Extracts( **extracts )

        return extracts

    def addStep( self, step: Step ):
        """
        Add a step to the workflow.

        Parameters
        ----------
        step : Step or dict
            A Step instance or dictionary with step configuration.
        """
        step = self._step_before( step )
        self.steps.append( step )

    def run( self, state: State ):
        """
        Execute all steps in the workflow.

        Steps are executed in order, with each step's outputs posted
        to the shared State. Steps may be skipped if their inputs
        match cached values from previous runs.

        Parameters
        ----------
        state : State
            The shared state object containing input data.

        Returns
        -------
        Any
            The output from the final step.
        """

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

        self._addOutputExtract( i, modelOutput )

        stateOutput = step.extractStateOutputFromModelOutput( modelOutput )
        step.postStateOutputToState( state, stateOutput )
        return state, stateOutput

    def _skipModel( self, i: int, modelInput ):
        skip        = False
        modelOutput = None

        skippable = all(( self.useExtracts, i in self.modelInputs, i in self.modelOutputs ))
        
        if skippable and self.modelInputs.equal( i, modelInput ):
            skip        = True
            modelOutput = self.modelOutputs.get( i )

        self._addInputExtract( i, modelInput )

        return skip, modelOutput

    def _addInputExtract( self, i: int, modelInput ):
        if self.populateExtracts:
            self.modelInputs.add( i, modelInput )

    def _addOutputExtract( self, i: int, modelOutput ):
        if self.populateExtracts:
            self.modelOutputs.add( i, modelOutput )

    def getModelInput( self, i: int ):
        return self.modelInputs.get( i )

    def getModelOutput( self, i: int ):
        return self.modelOutputs.get( i )

    def getModel( self, i: int ):
        step = self.steps[i]
        modelInput = self.getModelInput(i)
        return step.extractModelFromModelInput( modelInput )
