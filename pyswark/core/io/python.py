from pyswark.core.io import base


class Python(base.AbstractDataHandler):
    MODE_R = 'rb'

    def _read( self, fp, **kw ):
        return fp.locate()
