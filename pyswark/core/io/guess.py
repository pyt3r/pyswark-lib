from pyswark.lib.enum import AliasEnum, Alias
from pyswark.core.io.datahandler import DataHandler
from pyswark.core.models.uri.base import UriModel


def api( uri ):
    """  api for guesses based on uri """
    model  = UriModel( uri )
    ext    = model.Ext
    scheme = model.scheme

    klass = None

    try:
        klass = Ext.get( ext.full )

    except ValueError:
        klass = Scheme.get( scheme )

    finally:
        if not klass:
            raise ValueError( f"Handler not found for {uri=}" )

    return klass


# == guesses based on criteria embedded in the uri ==

class _AliasEnum( AliasEnum ):

    @classmethod
    def get( cls, name ):
        member = super().get( name )
        return member.klass

    @property
    def klass(self):
        return self.value.klass

    @property
    def path(self):
        return self.value.path


class Ext( _AliasEnum ):
    CSV       = DataHandler.DF_CSV,     Alias('csv')
    CSV_GZ    = DataHandler.DF_CSV_GZ,  Alias('csv.gz')
    PARQUET   = DataHandler.DF_PARQUET, Alias('parquet')
    JSON      = DataHandler.JSON,       Alias('json')
    PJSON     = DataHandler.PJSON,      Alias('pjson')
    GLUEDB    = DataHandler.GLUEDB,     Alias('gluedb')
    YAML_DOC  = DataHandler.YAML_DOC,   Alias([ 'yaml', 'yml', 'doc.yaml', 'doc.yml' ])
    YAML_DOCS = DataHandler.YAML_DOCS,  Alias([ 'docs.yaml', 'docs.yml' ])
    TEXT      = DataHandler.TEXT,       Alias(['html', 'shtml', 'py', 'txt', 'text', 'tex'])


class Scheme( _AliasEnum ):
    HTTP   = DataHandler.URL,    Alias(['http', 'https'])
    PYTHON = DataHandler.PYTHON, Alias('python')
