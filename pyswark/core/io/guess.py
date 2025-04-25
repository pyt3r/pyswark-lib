from pyswark.lib import enum
from pyswark.core.io.settings import Settings
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

class _Settings( enum.AliasEnum ):

    @classmethod
    def get( cls, name ):
        member = cls.getMember( name )
        return member.klass

    @property
    def klass(self):
        return self.value.klass

    @property
    def path(self):
        return self.value.path


class Ext( _Settings ):
    CSV     = Settings.DF_CSV, 'csv'
    CSV_GZ  = Settings.DF_CSV_GZ, 'csv.gz'
    PARQUET = Settings.DF_PARQUET, 'parquet'
    JSON    = Settings.JSON, 'json'
    PJSON   = Settings.PJSON, 'pjson'
    GLUEDB  = Settings.GLUEDB, 'gluedb'

    _YAML_DOC = Settings.YAML_DOC
    YAML      = _YAML_DOC, 'yaml'
    YML       = _YAML_DOC, 'yml'
    DOC_YAML  = _YAML_DOC, 'doc.yaml'
    DOC_YML   = _YAML_DOC, 'doc.yml'

    _YAML_DOCS = Settings.YAML_DOCS
    DOCS_YAML   = _YAML_DOCS, 'docs.yaml'
    DOCS_YML    = _YAML_DOCS, 'docs.yml'

    _TEXT = Settings.TEXT
    HTML  = _TEXT, 'html'
    SHTML = _TEXT, 'shtml'
    PY    = _TEXT, 'py'
    TXT   = _TEXT, 'txt'
    TEXT  = _TEXT, 'text'
    TEX   = _TEXT, 'tex'


class Scheme( _Settings ):
    HTTP   = Settings.URL, 'http'
    HTTPS  = Settings.URL, 'https'
    PYTHON = Settings.PYTHON, 'python'


