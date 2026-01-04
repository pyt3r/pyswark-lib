import yaml

from pyswark.core.io import base


class YamlDoc( base.AbstractDataHandler ):

    def _read( self, fp, **kw ):
        return self.readStatic( fp, **kw )

    @staticmethod
    def readStatic( data, **kw ):
        return yaml.safe_load( data, **kw )

    def _write( self, data, fp, **kw ):
        yaml.safe_dump( data, fp, **kw )


class YamlDocs( base.AbstractDataHandler ):

    def _read( self, fp, **kw ):
        return self.readStatic( fp, **kw )

    @staticmethod
    def readStatic( data, **kw):
        return list( yaml.safe_load_all( data ) )

    def _write( self, data, fp, **kw ):
        if isinstance( data, dict ):
            raise TypeError( f"Cannot write yaml documents for { data= }" )
        yaml.safe_dump_all( data, fp, **kw )
