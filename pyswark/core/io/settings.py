import pydoc
from pyswark.lib import enum
from pyswark.core import io
from pyswark.core.io import base


class Settings( enum.AliasEnum ):
    _ROOT       = io.__name__

    DF_CSV      = f'{ _ROOT }.df.Csv', "df.csv"
    DF_CSV_GZ   = f'{ _ROOT }.df.CsvGzip', "df.csv.gz"
    DF_PARQUET  = f'{ _ROOT }.df.Parquet', "df.parquet"
    JSON        = f'{ _ROOT }.json.Json', "json"
    PJSON       = f'{ _ROOT }.json.Pjson', "pjson"

    _YAML       = f'{ _ROOT }.yaml.YamlDoc'
    YAML        = _YAML, "yaml"
    YAML_DOC    = _YAML, "doc.yaml"

    YAML_DOCS   = f'{ _ROOT }.yaml.YamlDocs', "docs.yaml"
    PYTHON      = f'{ _ROOT }.python.Python', "python"
    URL         = f'{ _ROOT }.url.Url', "url"
    TEXT        = f'{ _ROOT }.text.Text', "file.text"
    GLUEDB      = f'{ _ROOT }.json.Pjson', "gluedb"

    @classmethod
    def get( cls, name ):
        klass = Settings.getMember( name ).klass
        if not ( klass and issubclass( klass, base.AbstractDataHandler ) ):
            raise ValueError( f"Invalid handler for entry = '{ name }' : '{ klass }'" )
        return klass

    @property
    def klass(self):
        return pydoc.locate( self.path )

    @property
    def path(self):
        return self.value


def get( name ):
    return Settings.get( name )
