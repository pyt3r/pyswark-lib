from pyswark.core.io import base

from pyswark.core.io.yaml import YamlDoc, YamlDocs
from pyswark.core.io.json import Json


class String( base.AbstractDataHandler ):

    @base.Log.decorate('r')
    def read( self, **kwargs ):
        string = self.uri.inputs.uri

        for datahandler in [ YamlDoc, YamlDocs, Json ]:
            try:
                return datahandler.readStatic( string, **kwargs )
            except Exception as e:
                continue
        raise ValueError( f"Unable to parse and read { string= }" )

    @base.Log.decorate('w')
    def write( self, data, **kwargs ):
        raise NotImplementedError