from pyswark.core.datahandler import base


class Text(base.AbstractDataHandler):
    """ i.e. /path/to/file.text, /file.txt, /file.anything """

    def _read( self, fp, **kw ):
        return fp.read( **kw )

    def _write( self, data, fp, **kw ):
        fp.write( data, **kw )
