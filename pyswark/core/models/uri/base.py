from functools import lru_cache
from typing import ClassVar
from pydantic import Field

from pyswark.core.models.uri import interface, guess, file, http, pyswark, python


class UriModel( interface.Model ):
    inputs  : interface.Inputs
    outputs : interface.Outputs = Field( default=None, description="" )
    _MODELS : ClassVar = {}

    @classmethod
    def function( cls, inputs ):
        model = cls._getModel( inputs.uri )
        return model.outputs

    @classmethod
    def register( cls, Model ):
        """ registers a uri model """
        scheme = Model.SCHEME
        if scheme in cls._MODELS:
            raise ValueError( f'{ scheme= } already registered' )
        cls._MODELS[ scheme ] = Model

    @classmethod
    @lru_cache()
    def _getModel( cls, uri ):
        for Model in cls._MODELS.values():
            if uri.startswith( f'{ Model.SCHEME }:' ):
                return Model( uri )
        return guess.Model( uri )

    def _getProperty( self, name ):
        model = self.getModel()
        return getattr( model, name )


_Models = [
    file.ModelGuess,
    file.ModelAbsolute,
    file.ModelRelative,
    python.Model,
    http.ModelHttp,
    http.ModelHttps,
    pyswark.Model,
]
[ UriModel.register( model ) for model in _Models ]