from pyswark.lib import enum
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

class AliasEnum( enum.AliasEnum ):

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


class Ext( AliasEnum ):
    CSV       = DataHandler.DF_CSV, 'csv'
    CSV_GZ    = DataHandler.DF_CSV_GZ, 'csv.gz'
    PARQUET   = DataHandler.DF_PARQUET, 'parquet'
    JSON      = DataHandler.JSON, 'json'
    PJSON     = DataHandler.PJSON, 'pjson'
    GLUEDB    = DataHandler.GLUEDB, 'gluedb'
    YAML_DOC  = DataHandler.YAML_DOC, [ 'yaml', 'yml', 'doc.yaml', 'doc.yml' ]
    YAML_DOCS = DataHandler.YAML_DOCS, [ 'docs.yaml', 'docs.yml' ]
    TEXT      = DataHandler.TEXT, ['html', 'shtml', 'py', 'txt', 'text', 'tex']


class Scheme( AliasEnum ):
    HTTP   = DataHandler.URL, ['http', 'https']
    PYTHON = DataHandler.PYTHON, 'python'
