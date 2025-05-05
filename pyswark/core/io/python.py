from pyswark.core.io import base


class Python(base.AbstractDataHandler):
    MODE_R = 'rb'

    def __init__( self, uri ):
        super().__init__( uri if uri.startswith( 'python:' ) else f'python:{ uri }' )

    def _read( self, fp, **kw ):
        return fp.locate()
