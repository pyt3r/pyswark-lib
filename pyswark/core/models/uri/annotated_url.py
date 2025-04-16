from typing import Annotated
from pydantic import AnyUrl, UrlConstraints

from pyswark.core.models.uri import schemes


def AnnotatedUrl( allowed_schemes=None ):
    """ makes an annotated url type """
    args = [ AnyUrl ]

    if allowed_schemes:
        err = sorted(set( allowed_schemes ) - set(schemes.ALLOWED))
        assert not err, f"invalid scheme={ err }"
        args += [ UrlConstraints( allowed_schemes=allowed_schemes ) ]
    else:
        args += [ ..., ]

    return Annotated[ tuple( args ) ]

