import pydoc
from pyswark.lib.enum import AliasEnum, Alias
from pyswark.core import io
from pyswark.core.io import base


class DataHandler( AliasEnum ):
    _ROOT       = io.__name__

    DF_CSV      = f'{ _ROOT }.df.Csv', Alias("df.csv")
    DF_CSV_GZ   = f'{ _ROOT }.df.CsvGzip', Alias("df.csv.gz")
    DF_PARQUET  = f'{ _ROOT }.df.Parquet', Alias("df.parquet")
    JSON        = f'{ _ROOT }.json.Json', Alias("json")
    PJSON       = f'{ _ROOT }.json.Pjson', Alias("pjson")
    YAML_DOC    = f'{ _ROOT }.yaml.YamlDoc', Alias([ "yaml", "doc.yaml" ])
    YAML_DOCS   = f'{ _ROOT }.yaml.YamlDocs', Alias("docs.yaml")
    PYTHON      = f'{ _ROOT }.python.Python', Alias("python")
    URL         = f'{ _ROOT }.url.Url', Alias("url")
    TEXT        = f'{ _ROOT }.text.Text', Alias("file.text")
    GLUEDB      = f'{ _ROOT }.json.Pjson', Alias("gluedb")

    @classmethod
    def get( cls, name ):
        klass = super().get( name ).klass
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
    return DataHandler.get(name)
