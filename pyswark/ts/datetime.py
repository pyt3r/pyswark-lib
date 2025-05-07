from pydantic import Field, field_validator, model_validator
from typing import Union, TypeVar
import numpy as np
import datetime
from dateutil import parser, tz

from pyswark.core.models import converter, xputs


NumpyArray = TypeVar( 'numpy.ndarray' )
DtypeType  = Union[ str, None ]
TznameType = Union[ str, None ]

class Datetime( xputs.BaseInputs ):
    data     : str
    dtype    : DtypeType = Field( default=None )
    tzname   : TznameType = Field( default=None )

    @classmethod
    def now( cls, tzname='UTC' ):
        return cls( datetime.datetime.now( datetime.UTC ), 's', 'UTC' ).toTimezone( tzname )

    @property
    def dt(self):
        return self._data

    @property
    def datetime(self):
        return parser.parse( str( self.dt ))

    @field_validator( 'data', mode='before' )
    def before_data( cls, data ) -> str:
        return str( data ) if data is not None else data

    @field_validator( 'dtype', mode='before' )
    def before_dtype( cls, dtype ):
        return str( dtype ) if dtype is not None else dtype

    @model_validator( mode='after' )
    def after( self ):
        self.tzname = self.after_tzname( self.tzname, self.data )
        dtype       = self.after_dtype( self.dtype )
        data, dtype = self.after_data_dtype( self.data, dtype )

        self.data   = str( data )
        self._data  = data
        self.dtype  = str( dtype ) if dtype else dtype
        return self

    @classmethod
    def after_tzname( cls, tzname, data ):
        try:
            _tzname = parser.parse( data, tzinfos=cls._getTzInfos() ).tzname()
        except:
            _tzname = None

        if tzname and _tzname and tzname != _tzname:
            raise ValueError(f"Mismatch between { tzname= } and { _tzname }")

        return tzname or _tzname

    @staticmethod
    def after_dtype( dtype ):
        if dtype in 'Y M W D h m s ms us ns ps fs as'.split():
            dtype = np.dtype(f'datetime64[{ dtype }]')
        elif dtype:
            dtype = np.dtype( dtype )
        return dtype

    @classmethod
    def after_data_dtype( cls, data, dtype ):
        try:
            dt     = np.datetime64( data )
            _dtype = dt.dtype
        except:
            dt     = parser.parse( data )
            dt     = dt.combine( dt.date(), dt.time() ) # remove tzinfo
            dt     = np.datetime64( str(dt) )
            _dtype = None

        if dtype and _dtype and _dtype < dtype:
            raise ValueError(f"{ data= } passed with mismatching { dtype= }")

        dtype = dtype or _dtype
        dt = dt.astype( dtype ) if dtype else dt

        return ( dt, dtype )

    def toDtype( self, dtype ):
        if self.after_dtype( self.dtype ) == self.after_dtype( dtype ):
            return self
        return Datetime( self.data, dtype, self.tzname )

    def toTimezone( self, tzname ):
        if self.tzname == tzname:
            return self

        currTime   = self.dt
        currTzname = self.tzname

        currTimeUTC = currTime - self._getOffsetUTC( currTzname )
        currTime    = currTimeUTC + self._getOffsetUTC( tzname )

        return Datetime( currTime, currTime.dtype, tzname )

    @staticmethod
    def _getOffsetUTC( tzname ):
        return {
            "UTC": np.timedelta64(  0 ),
            "EST": np.timedelta64( -4, 'h' ),
            "EDT": np.timedelta64( -4, 'h' ),
            "CST": np.timedelta64( -6, 'h' ),
            "CDT": np.timedelta64( -5, 'h' ),
            "MST": np.timedelta64( -7, 'h' ),
            "MDT": np.timedelta64( -6, 'h' ),
            "PST": np.timedelta64( -8, 'h' ),
            "PDT": np.timedelta64( -7, 'h' ),
        }[ tzname ]

    @staticmethod
    def _getTzInfos():
        return {
            'UTC': tz.gettz('UTC'),
            'EST': tz.gettz('America/New_York'),
            'EDT': tz.gettz('America/New_York'),
            'CST': tz.gettz('America/Chicago'),
            'CDT': tz.gettz('America/Chicago'),
            'MST': tz.gettz('America/Denver'),
            'MDT': tz.gettz('America/Denver'),
            'PST': tz.gettz('America/Los_Angeles'),
            'PDT': tz.gettz('America/Los_Angeles'),

            # International examples
            'GMT': tz.gettz('Etc/GMT'), # Greenwich Mean Time
            'CET': tz.gettz('Europe/Paris'),
            'CEST': tz.gettz('Europe/Paris'),
            'IST': tz.gettz('Asia/Kolkata'),
            'JST': tz.gettz('Asia/Tokyo'),
            'AEST': tz.gettz('Australia/Sydney'),
            'AEDT': tz.gettz('Australia/Sydney'),
            'NZST': tz.gettz('Pacific/Auckland'),
            'NZDT': tz.gettz('Pacific/Auckland'),
        }


class Inputs( xputs.BaseInputs ):
    base    : Union[ NumpyArray, str, Datetime ]
    periods : Union[ NumpyArray, tuple[ int ], list[ int ] ] = Field( default_factory=lambda: [0] )

    @field_validator( 'base', mode='before')
    def _base( cls, base ):

        if isinstance( base, Datetime ):
            return base

        if isinstance( base, str ):
            return Datetime( base )

        if isinstance( base, dict ):
            return Datetime( **base )

        return base

    @model_validator( mode='after' )
    def after( self ):

        base = self.base
        periods = self.periods

        if isinstance( base, Datetime ) and isinstance( periods, list ):
            pass

        else:
            base, periods = self._after( base, periods )
            self.base = base
            self.periods = periods

        return self

    def _after(self, base, periods ):

        if isinstance( base, ( list, tuple, np.ndarray )):
            periods = [ Datetime(e).dt for e in base ]
            base = periods[0]

        base = base if isinstance( base, Datetime ) else Datetime( base )
        periods = np.asarray( periods )

        if np.issubdtype( periods.dtype, np.timedelta64 ):
            periods = ( base.dt + periods ).astype( base.dtype )

        if np.issubdtype( periods.dtype, np.datetime64 ):
            periods = ( periods - base.dt )

        valid = np.issubdtype( periods.dtype, int ) or np.issubdtype( periods.dtype, np.timedelta64 )
        if not valid:
            raise TypeError( f"{ periods.dtype= } must be int or timedelta ")

        periods = periods.astype( int )
        isSorted = periods[1:] - periods[:-1]
        if ( isSorted < 0 ).any():
            raise ValueError( "periods must be sorted" )

        return base, periods.tolist()


class DatetimeList( converter.ConverterModel ):
    inputs : Inputs

    def __len__(self):
        return len( self.dt )

    @property
    def dt(self):
        return self.outputs['dt']

    @property
    def basedt(self):
        return self.outputs['basedt']

    @property
    def deltas(self):
        return self.outputs['deltas']

    @property
    def dtype(self):
        return self.inputs.base.dtype

    def astype(self, dtype):
        base = self.inputs.base
        to   = base.after_dtype( dtype )
        new  = self.dt.astype( to )
        return DatetimeList(new)

    def resample( self, to ):
        """ return sampled Datetimelist """

        base = self.inputs.base
        curr = base.after_dtype( base.dtype )
        to   = base.after_dtype( to )
        if not to:
            raise ValueError( f"invalid sampling size: { to= }" )

        new = self.dt
        if to < curr: # downsample
            new = new.astype( to ) + 1

        elif to > curr: # upsample
            oldRes = new + 1
            newRes = new.astype( to )
            offset = ( newRes - newRes ) + 1
            new    = oldRes - offset

        return DatetimeList(new)

    @staticmethod
    def convert( inputs: Inputs ) -> dict[ str, Union[ Datetime, np.ndarray ]]:
        results = {
            'basedt' : inputs.base.dt,
            'deltas' : np.asarray( inputs.periods ), }
        return {
            'dt' : results['basedt'] + results['deltas'],
            **results, }
