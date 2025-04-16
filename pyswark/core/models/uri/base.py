from typing import Annotated, Union
from pydantic import create_model

from pyswark.core.models.uri import root, root_all


def createUriModel( subModels ):
    """ dynamically create the Uri model from submodels """

    AnyUri = Annotated[ Union[ subModels ], ...]

    return create_model(
        "UriModel",
        __base__ = root.UriRootModel,
        root  = ( AnyUri, ... )
    )


UriModel = createUriModel( root_all.get() )