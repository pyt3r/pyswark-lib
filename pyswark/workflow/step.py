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
        model = self.extractModel( state )
        modelOutput = model.run()
        outputData = self.extractOutputData( modelOutput )
        self.loadOutputData( state, outputData )
        return outputData

    def extractModel( self, state ):
        Model = self._getModelClass()
        inputData = self.extractInputData( state )
        return Model( **inputData )

    def getExternalInputNames( self ):
        return list( self.inputs.keys() )
        
    def getInternalInputNames( self ):
        return list( self.inputs.values() )

    def getInternalOutputNames( self ):
        return list( self.outputs.keys() )

    def getExternalOutputNames( self ):
        return list( self.outputs.values() )

    def extractInputData( self, state ):
        """ extracts inputs from state """
        inputData = state.extract( self.getExternalInputNames() )
        return dict( zip( self.getInternalInputNames(), inputData ))
        
    def loadOutputData( self, state, outputData ):
        """ loads output to state """
        state.load( outputData )

    def extractOutputData( self, modelOutput ):
        """ extracts outputs from model """
        internalToExternal = zip( self.getInternalOutputNames(), self.getExternalOutputNames() )
        return { e: modelOutput[i] for i, e in internalToExternal }
