from typing import Any
from pyswark.core.models import primitive, collection


def Infer( inputs: Any ):
    """ infers a model for a given input """
    Models = [ primitive.Infer, collection.Infer ]

    for Model in Models:
        if Model.inScope( inputs ):
            return Model( inputs )
        
    raise ValueError( f"could not infer type={type(inputs)}" )
