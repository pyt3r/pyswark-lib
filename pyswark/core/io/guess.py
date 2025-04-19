from pyswark.core import settings
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

class _Settings( settings.Settings ):

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
    CSV     = ( 'csv'    , Settings.DF_CSV )
    CSV_GZ  = ( 'csv.gz' , Settings.DF_CSV_GZ )
    PARQUET = ( 'parquet', Settings.DF_PARQUET )
    JSON    = ( 'json'   , Settings.JSON )
    PJSON   = ( 'pjson'  , Settings.PJSON )
    GLUEDB  = ( 'gluedb' , Settings.GLUEDB )

    _YAML_DOC = Settings.YAML_DOC
    YAML      = ( 'yaml'    , _YAML_DOC )
    YML       = ( 'yml'     , _YAML_DOC )
    DOC_YAML  = ( 'doc.yaml', _YAML_DOC )
    DOC_YML   = ( 'doc.yml' , _YAML_DOC )

    _YAML_DOCS = Settings.YAML_DOCS
    DOCS_YAML   = ( 'docs.yaml', _YAML_DOCS )
    DOCS_YML    = ( 'docs.yml' , _YAML_DOCS )

    _TEXT = Settings.TEXT
    HTML  = ( 'html' , _TEXT )
    SHTML = ( 'shtml', _TEXT )
    PY    = ( 'py'   , _TEXT )
    TXT   = ( 'txt'  , _TEXT )
    TEXT  = ( 'text' , _TEXT )
    TEX   = ( 'tex'  , _TEXT )


class Scheme( _Settings ):
    HTTP   = ( 'http'  , Settings.URL )
    HTTPS  = ( 'https' , Settings.URL )
    PYTHON = ( 'python', Settings.PYTHON )


