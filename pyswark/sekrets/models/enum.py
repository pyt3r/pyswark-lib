from pyswark.lib.aenum import AliasEnum, Alias
from pyswark.core.io import api


def _Model( name, *aliases ):
    uri = f'python://pyswark.sekrets.models.{ name }.Sekret'
    return uri, Alias( name, *aliases )


class Models( AliasEnum ):
    GENERIC   = _Model( 'generic' )
    GDRIVE2   = _Model( 'gdrive2' )
    
    @property
    def klass( self ):        
        return api.read( self.value )
