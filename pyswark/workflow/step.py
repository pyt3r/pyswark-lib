"""
Workflow Step
=============

This module defines the Step class, the fundamental unit of work in a
workflow. Each Step specifies a model to run and mappings between
workflow state and model inputs/outputs.
"""

from typing import Any, Dict, Optional, Union
from pydantic import field_validator
import pydoc
from pyswark.lib.pydantic import base
from pyswark.core.models.infer import Infer

from pyswark.workflow.state import State


class Step( base.BaseModel ):
    """
    A single unit of work in a Workflow.

    A Step defines:
    
    - A model (class) to instantiate and run
    - Input mappings: state names → model input names
    - Output mappings: model output names → state names

    Parameters
    ----------
    model : str
        Fully-qualified Python path to the model class
        (e.g., ``"mymodule.MyModel"``).
    inputs : dict[str, str]
        Mapping from state variable names to model input names.
        ``{state_name: model_input_name}``.
    outputs : dict[str, str]
        Mapping from model output names to state variable names.
        ``{model_output_name: state_name}``.

    Example
    -------
    >>> step = Step(
    ...     model='mymodule.PreprocessModel',
    ...     inputs={'raw_data': 'data'},      # state 'raw_data' → model 'data'
    ...     outputs={'processed': 'clean'}    # model 'processed' → state 'clean'
    ... )
    """
    model   : str
    inputs  : Dict[ str, str ]
    outputs : Dict[ str, str ]

    @field_validator( 'model', mode='before' )
    def _model( cls, model: str ):
        return model if isinstance( model, str ) else model.getUri()

    def _getModelClass( self ):
        return pydoc.locate( self.model )

    def run( self, state ):
        """
        Execute this step using data from state.

        Extracts inputs from state, runs the model, and posts
        outputs back to state.

        Parameters
        ----------
        state : State
            The shared state object.

        Returns
        -------
        dict
            The step's outputs (also posted to state).
        """
        stateInput  = self.extractStateInputFromState( state )
        modelInput  = self.extractModelInputFromStateInput( stateInput )
        model       = self.extractModelFromModelInput( modelInput )
        modelOutput = model.run()
        stateOutput = self.extractStateOutputFromModelOutput( modelOutput )
        self.postStateOutputToState( state, stateOutput )
        return stateOutput

    def extractModelFromModelInput( self, inputData ):
        Model = self._getModelClass()
        return Model( **inputData )

    def getStateInputNames( self ):
        return list( self.inputs.keys() )
        
    def getModelInputNames( self ):
        return list( self.inputs.values() )

    def getModelOutputNames( self ):
        return list( self.outputs.keys() )

    def getStateOutputNames( self ):
        return list( self.outputs.values() )

    def extractStateInputFromState( self, state ):
        """ extracts inputs from state """
        return [ state.extract( name ) for name in self.getStateInputNames() ]

    def extractModelInputFromStateInput( self, stateInput ):
        """ extracts inputs from state """
        return dict( zip( self.getModelInputNames(), stateInput ))
        
    def postStateOutputToState( self, state, outputData ):
        """ loads output to state """
        for name, contents in outputData.items():
            state.post( name, contents )

    def extractStateOutputFromModelOutput( self, modelOutput ):
        """ extracts outputs from model """
        internalToExternal = zip( self.getModelOutputNames(), self.getStateOutputNames() )
        return { e: modelOutput[i] for i, e in internalToExternal }
