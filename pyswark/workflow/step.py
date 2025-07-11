from typing import Any, Dict, Optional, Union
from pydantic import field_validator
import pydoc
from pyswark.lib.pydantic import base


class Step( base.BaseModel ):
    model   : str
    inputs  : Dict[ str, str ]
    outputs : Dict[ str, str ]

    @field_validator( 'model', mode='before' )
    def _model( cls, model: str ):
        return model if isinstance( model, str ) else model.getUri()

    def _getModelClass( self ):
        return pydoc.locate( self.model )

    def run( self, state ):
        """ runs the step """
        stateInput  = self.extractStateInputFromState( state )
        modelInput  = self.extractModelInputFromStateInput( stateInput )
        model       = self.extractModelFromModelInput( modelInput )
        modelOutput = model.run()
        stateOutput = self.extractStateOutputFromModelOutput( modelOutput )
        self.loadStateOutputToState( state, stateOutput )
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
        return state.extract( self.getStateInputNames() )

    def extractModelInputFromStateInput( self, stateInput ):
        """ extracts inputs from state """
        return dict( zip( self.getModelInputNames(), stateInput ))
        
    def loadStateOutputToState( self, state, outputData ):
        """ loads output to state """
        state.load( outputData )

    def extractStateOutputFromModelOutput( self, modelOutput ):
        """ extracts outputs from model """
        internalToExternal = zip( self.getModelOutputNames(), self.getStateOutputNames() )
        return { e: modelOutput[i] for i, e in internalToExternal }
