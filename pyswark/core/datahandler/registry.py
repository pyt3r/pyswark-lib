import pydoc

from pyswark.core.datahandler import base


class Handler:
    DF_CSV      = "df.csv"
    DF_CSV_GZ   = "df.csv.gz"
    DF_PARQUET  = "df.parquet"
    JSON        = "json"
    PJSON       = "pjson"
    YAML        = "yaml"
    YAML_DOC    = "doc.yaml"
    YAML_DOCS   = "docs.yaml"
    PYTHON      = "python"
    URL         = "url"
    TEXT        = "file.ext"
    GLUEDB      = "gluedb"


_ROOT = 'pyswark.core.datahandler'
_REGISTRY = {
    Handler.DF_CSV      : f"{ _ROOT }.df.Csv",
    Handler.DF_CSV_GZ   : f"{ _ROOT }.df.CsvGzip",
    Handler.DF_PARQUET  : f"{ _ROOT }.df.Parquet",
    Handler.JSON        : f"{ _ROOT }.json.Json",
    Handler.PJSON       : f"{ _ROOT }.json.Pjson",
    Handler.YAML        : f"{ _ROOT }.yaml.YamlDoc",
    Handler.YAML_DOC    : f"{ _ROOT }.yaml.YamlDoc",
    Handler.YAML_DOCS   : f"{ _ROOT }.yaml.YamlDocs",
    Handler.GLUEDB      : f"{ _ROOT }.json.Pjson",
    Handler.PYTHON      : f"{ _ROOT }.python.Python",
    Handler.URL         : f"{ _ROOT }.url.Url",
    Handler.TEXT        : f"{ _ROOT }.text.Text",
}


def get( name ):
    path  = _REGISTRY[ name ]
    klass = pydoc.locate( path )
    msg   = f"Invalid handler for entry = '{ name }' : '{ path }'"
    assert klass and issubclass(klass, base.AbstractDataHandler), msg
    return klass
