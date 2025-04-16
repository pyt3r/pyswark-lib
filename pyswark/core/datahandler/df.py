import pandas

from pyswark.core.datahandler import decorate, base


class Kwargs(decorate.Kwargs):

    _CSV = {
        'r': { 'index_col': 0, },
        'w': { 'index': True },
    }
    _CSV_GZIP = {
        'r': { **_CSV['r'], 'compression': 'gzip' },
        'w': { **_CSV['w'], 'compression': 'gzip' },
    }

    PAYLOAD = {
        "Csv"     : _CSV,
        "CsvGzip" : _CSV_GZIP,
        "Parquet" : { 'r': {}, 'w': {} },
    }


class Csv(base.AbstractDataHandler):

    @Kwargs.decorate('r')
    def _read( self, fp, **kw ):
        return pandas.read_csv( fp, **kw )

    @Kwargs.decorate('w')
    def _write( self, data, fp, **kw ):
        data.to_csv( fp, **kw )


class CsvGzip( Csv ):
    """ csv gzip """


class Parquet(base.AbstractDataHandler):
    MODE_R = 'rb'
    MODE_W = 'wb'

    @Kwargs.decorate('r')
    def _read( self, fp, **kw ):
        return pandas.read_parquet( fp.path )

    @Kwargs.decorate('w')
    def _write( self, data, fp, **kw ):
        data.to_parquet( fp, **kw )
