import json

from pyswark.core.datahandler import decorate, base
from pyswark.lib.pydantic.ser_des import fromDict, toDict


class Kwargs(decorate.Kwargs):

    PAYLOAD = {
        "Json"  : { 'r': {}, 'w': {} },
        "Pjson" : { 'r': {}, 'w': {} },
    }


class Json(base.AbstractDataHandler):
    MODE_R = 'r'
    MODE_W = 'w'

    @Kwargs.decorate('r')
    def _read( self, fp, **kw ):
        return json.load( fp, **kw )

    @Kwargs.decorate('w')
    def _write( self, data, fp, **kw ):
        json.dump( data, fp, **kw )


class Pjson( Json ):

    @Kwargs.decorate( 'r' )
    def _read( self, fp, **kw ):
        dic = super()._read( fp, **kw )
        return fromDict( dic )

    @Kwargs.decorate( 'w' )
    def _write( self, data, fp, **kw ):
        dic = toDict( data )
        super()._write( dic, fp, **kw )
