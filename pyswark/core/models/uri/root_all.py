from pyswark.core.models.uri import root
from pyswark.core.models.uri import root_extra


def get():
    return (
        root.FileAbsolute,
        root.FileRelative,
        root.Python,
        root.Http,
        root_extra.ResolvableHttp,
        root_extra.ResolvableFile,
    )
