from pydantic import Field, ValidationError

from pyswark.core.models.uri import interface, generic, file, http


class Model( interface.Model ):
    inputs  : interface.Inputs
    outputs : interface.Outputs = Field( default=None, description="" )

    def __new__( cls, uri ):
        try:
            model = generic.Model( uri )
            if model.host:
                if not model.path and not model.Ext:
                    return _guess( uri )
                model = http.ModelGuess( uri )
            return model

        except ValidationError:
            return file.ModelGuess( f'file:{ uri }' )


def _guess( uri ):
    if uri.endswith((
        '.com',
        '.net',
        '.org',
        '.edu',
        '.gov',
        '.info',
        '.biz',
        '.io',
        '.co',
        '.app',
        '.dev',
        '.ai',
        '.cloud',
        '.tech',
    )):
        return http.ModelGuess( uri )
    else:
        return file.ModelGuess( f'file:{ uri }' )
