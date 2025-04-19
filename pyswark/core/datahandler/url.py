from pyswark.core.datahandler import base


class Url( base.AbstractDataHandler ):

    def _read( self, fp, **kw ):
        return fp.read( **kw )
