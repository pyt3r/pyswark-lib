import unittest

from pyswark.ts.tsvector import TsVector


class TestCase( unittest.TestCase ):

    def test_merge_two_monthly_tsvectors( self ):
        periods = [ 0, 2, 4, 6, 8, 10 ]

        v1 = TsVector(
            index=['2025-01', '2025-03', '2025-05', '2025-07', '2025-09', '2025-11'],
            values=[ 1.1, 3.3, 5.5, 7.7, 9.9, 11.11 ],
        )

        v2 = TsVector(
            index={ 'base' : '2025-02', 'periods' : periods },
            values=[  2.2, 4.4, 6.6, 8.8, 10.10, 12.12 ],
        )
