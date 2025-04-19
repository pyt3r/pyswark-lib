import pydoc

from pyswark.core import settings
from pyswark.core.datahandler import base


class Settings( settings.Settings ):
    _ROOT       = 'pyswark.core.datahandler'

    DF_CSV      = ( "df.csv"    , f'{ _ROOT }.df.Csv' )
    DF_CSV_GZ   = ( "df.csv.gz" , f'{ _ROOT }.df.CsvGzip' )
    DF_PARQUET  = ( "df.parquet", f'{ _ROOT }.df.Parquet' )
    JSON        = ( "json"      , f'{ _ROOT }.json.Json' )
    PJSON       = ( "pjson"     , f'{ _ROOT }.json.Pjson' )

    _YAML       = f'{ _ROOT }.yaml.YamlDoc'
    YAML        = ( "yaml"      , _YAML )
    YAML_DOC    = ( "doc.yaml"  , _YAML )

    YAML_DOCS   = ( "docs.yaml" , f'{ _ROOT }.yaml.YamlDocs' )
    PYTHON      = ( "python"    , f'{ _ROOT }.python.Python' )
    URL         = ( "url"       , f'{ _ROOT }.url.Url' )
    TEXT        = ( "file.text" , f'{ _ROOT }.text.Text' )
    GLUEDB      = ( "gluedb"    , f'{ _ROOT }.json.Pjson' )

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
