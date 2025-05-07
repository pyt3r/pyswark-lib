import unittest
import numpy as np
import datetime

from pyswark.lib.pydantic import ser_des
from pyswark.ts.datetime import Datetime, DatetimeList


class DatetimeTestCase( unittest.TestCase ):

    def test_inputs_with_implicit_UTC_tzname(self):
        model = Datetime("Wednesday, 08-Jan-25 12:30:00 UTC")
        self.assertEqual( model.data, '2025-01-08T12:30:00' )
        self.assertEqual( model.tzname, 'UTC' )
        self.assertIsNone( model.dtype )

    def test_model_with_implicit_UTC_tzname_and_explicit_dtype(self):
        model = Datetime(data="Wednesday, 08-Jan-25 12:30:00 UTC", dtype='M')
        self.assertEqual( model.data, '2025-01' )
        self.assertEqual( model.tzname, 'UTC' )
        self.assertEqual( model.dtype, 'datetime64[M]' )

    def test_model_with_implicit_EST_tzname(self):
        model = Datetime("Wednesday, 08-Jan-25 12:30:00 EST", 'm')
        self.assertEqual( model.data, '2025-01-08T12:30' )
        self.assertEqual( model.tzname, 'EST' )
        self.assertEqual( model.dtype, 'datetime64[m]' )

    def test_model_with_implicit_EST_tzname_and_explicit_UTC(self):
        with self.assertRaises( ValueError ):
            Datetime(data="Wednesday, 08-Jan-25 12:30:00 EST", tzname="UTC")

    def test_model_with_explicit_tzname(self):
        model = Datetime(data="Wednesday, 08-Jan-25 12:30:00", dtype='D', tzname='EST')
        self.assertEqual( model.data, '2025-01-08' )
        self.assertEqual( model.tzname, 'EST' )
        self.assertEqual( model.dtype, 'datetime64[D]' )

    def test_from_data(self):
        model = Datetime(data=2025)
        self.assertIsInstance( model.dt, np.datetime64 )

    def test_from_datetime64(self):
        data  = np.datetime64('2025-01')
        model = Datetime(data=data)
        self.assertEqual( model.dt, data )

    def test_from_datetime(self):
        data  = datetime.datetime(2025, 1, 1)
        model = Datetime(data=data)
        self.assertEqual( model.dt, data )

    def test_toTimezone(self):
        model = Datetime(data="Wednesday, 08-Jan-25 12:30:00 UTC")
        self.assertEqual( str(model.dt), '2025-01-08T12:30:00' )

        modelEST = model.toTimezone( "EST" )
        self.assertEqual( str(modelEST.dt), '2025-01-08T07:30:00' )

        modelPST = modelEST.toTimezone( "PST" )
        self.assertEqual( str(modelPST.dt), '2025-01-08T04:30:00' )

    def test_mismatching_dtype(self):
        with self.assertRaises( ValueError ):
            Datetime(data=2025, dtype='s')

    def test_toDtype(self):
        model = Datetime(data="Wednesday, 08-Jan-25 12:30:00 UTC")
        self.assertEqual( str(model.dt), '2025-01-08T12:30:00' )

        model2 = model.toDtype( 'm' )
        self.assertEqual( str(model2.dt), '2025-01-08T12:30' )

        model2 = model.toDtype( 'h' )
        self.assertEqual( str(model2.dt), '2025-01-08T12' )

        model2 = model.toDtype( np.dtype('<M8[M]') )
        self.assertEqual( str(model2.dt), '2025-01' )

        model2 = model.toDtype( 'datetime64[Y]' )
        self.assertEqual( str(model2.dt), '2025' )

    def test_ser_des(self):
        model = Datetime(data=2025)
        ser   = ser_des.toJson( model )
        des   = ser_des.fromJson( ser )
        self.assertEqual( model.dt, des.dt )


class DatetimesTestCase( unittest.TestCase ):

    def test_from_base_and_timedelta(self):
        freq = 'Y'
        inputs = {
            'base' : { 'data': 2020 },
            'periods' : np.array([ 0, 1, 1, 2 ], dtype=f'timedelta64[{freq}]'),
        }
        model = DatetimeList(inputs=inputs)
        np.testing.assert_array_equal( model.dt, np.array(['2020', '2021', '2021', '2022'], dtype='datetime64[Y]') )

    def test_from_base_and_timedelta_mismatching(self):
        freq = 'M'
        inputs = {
            'base' : 2020,
            'periods' : np.array([ 0, 1, 1, 2 ], dtype=f'timedelta64[{freq}]'),
        }
        model = DatetimeList(inputs=inputs)
        np.testing.assert_array_equal( model.dt, np.array(['2020']*4, dtype='datetime64[Y]') )

    def test_from_base_and_list_1(self):
        inputs = {
            'base' : Datetime(data=2020),
            'periods' : [ 0, 1, 1, 2 ],
        }
        model = DatetimeList(inputs=inputs)
        np.testing.assert_array_equal( model.dt, np.array(['2020', '2021', '2021', '2022'], dtype='datetime64[Y]') )

    def test_from_base_and_list_2(self):
        inputs = {
            'base' : {"data": 2020},
            'periods' : [ 0, 1, 1, 2 ],
        }
        model = DatetimeList(inputs=inputs)
        np.testing.assert_array_equal( model.dt, np.array(['2020', '2021', '2021', '2022'], dtype='datetime64[Y]') )

    def test_from_base(self):
        inputs = { 'base' : 2020 }
        model = DatetimeList(inputs=inputs)
        np.testing.assert_array_equal( model.dt, np.array(['2020'], dtype='datetime64[Y]') )
        np.testing.assert_array_equal( model.deltas, np.array([0]) )

    def test_from_alist(self):
        inputs = [2020, 2021, 2022, 2022]
        model = DatetimeList(inputs)
        self.assertEqual( model.basedt, np.datetime64('2020', 'Y') )
        np.testing.assert_array_equal( model.deltas, np.array([0, 1, 2, 2]) )

    def test_from_array(self):
        inputs = np.array(['2025-01', '2025-02', '2025-03'], dtype=np.datetime64)
        model = DatetimeList(inputs)
        self.assertEqual( model.basedt, np.datetime64('2025-01', 'M') )
        np.testing.assert_array_equal( model.deltas, np.array([0, 1, 2]) )


    def test_ser_des(self):
        model = DatetimeList([2020, 2021, 2022, 2023])
        ser   = ser_des.toJson( model )
        des   = ser_des.fromJson( ser )
        self.assertEqual( model.basedt, des.basedt )
        np.testing.assert_array_equal( model.dt, des.dt )
        np.testing.assert_array_equal( model.deltas, des.deltas )


class TestSampling( unittest.TestCase ):

    def test_resample_from_months_to_months(self):
        M1 = DatetimeList(['2025-01', '2025-02', '2025-03'])
        M2 = M1.resample('M')
        np.testing.assert_array_equal( M2.dt, np.array(['2025-01', '2025-02', '2025-03'], dtype='datetime64[M]') )

    def test_convert_from_months_to_months(self):
        M1 = DatetimeList(['2025-01', '2025-02', '2025-03'])
        M2 = M1.astype('M')
        np.testing.assert_array_equal( M2.dt, np.array(['2025-01', '2025-02', '2025-03'], dtype='datetime64[M]') )

    def test_resample_down_from_months_to_years(self):
        M = DatetimeList(['2025-01', '2025-02', '2025-03'])
        Y = M.resample('Y')
        np.testing.assert_array_equal( Y.dt, np.array(['2026', '2026', '2026'], dtype='datetime64[Y]') )

    def test_convert_from_months_to_years(self):
        M = DatetimeList(['2025-01', '2025-02', '2025-03'])
        Y = M.astype('Y')
        np.testing.assert_array_equal( Y.dt, np.array(['2025', '2025', '2025'], dtype='datetime64[Y]') )

    def test_resample_up_from_months_to_days(self):
        M = DatetimeList(['2025-01', '2025-02', '2025-03'])
        D = M.resample('D')
        np.testing.assert_array_equal( D.dt, np.array(['2025-01-31', '2025-02-28', '2025-03-31'], dtype='datetime64[D]') )

    def test_convert_from_months_to_days(self):
        M = DatetimeList(['2025-01', '2025-02', '2025-03'])
        D = M.astype('D')
        np.testing.assert_array_equal( D.dt, np.array(['2025-01-01', '2025-02-01', '2025-03-01'], dtype='datetime64[D]') )

    def test_resample_up_from_months_to_seconds(self):
        M = DatetimeList(['2025-01', '2025-02', '2025-03'])
        S = M.resample('s')
        np.testing.assert_array_equal( S.dt, np.array(['2025-01-31T23:59:59', '2025-02-28T23:59:59', '2025-03-31T23:59:59'], dtype='datetime64[s]') )
