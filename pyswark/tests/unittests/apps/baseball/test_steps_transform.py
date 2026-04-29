import unittest
from datetime import datetime

from pyswark.apps.baseball.steps.parse     import ParsedGames, GameRaw
from pyswark.apps.baseball.steps.transform import TransformModel, CleanGames, Game


def _raw( date, a, aS, h, hS ):
    return GameRaw( date=date, awayTeam=a, awayScore=str(aS), homeTeam=h, homeScore=str(hS) )


class TestConvert( unittest.TestCase ):

    def test_converts_scores_to_int_and_date_to_datetime( self ):
        parsed = ParsedGames( records=[ _raw( 'Thursday, March 30, 2023', 'A', 7, 'B', 2 ) ])
        clean  = TransformModel.convert( parsed )
        self.assertIsInstance( clean, CleanGames )
        self.assertEqual( len( clean.records ), 1 )

        g = clean.records[ 0 ]
        self.assertIsInstance( g, Game )
        self.assertEqual( g.date,      datetime( 2023, 3, 30 ))
        self.assertEqual( g.awayScore, 7 )
        self.assertEqual( g.homeScore, 2 )

    def test_raises_on_non_numeric_score( self ):
        parsed = ParsedGames( records=[ _raw( 'Thursday, March 30, 2023', 'A', 'X', 'B', 2 ) ])
        with self.assertRaises( Exception ):
            TransformModel.convert( parsed )


def _pair( a, b ):
    """Two games: a@b and b@a, so both teams appear on both sides."""
    return [
        _raw( 'Thursday, March 30, 2023', a, 1, b, 2 ),
        _raw( 'Friday, March 31, 2023',   b, 3, a, 4 ),
    ]


class TestValidateRoster( unittest.TestCase ):

    def test_passes_when_home_and_away_match_and_count_matches( self ):
        teams = [ f'Team{ i }' for i in range( 30 ) ]
        raws  = []
        for i, a in enumerate( teams ):
            b = teams[ ( i + 1 ) % len( teams ) ]
            raws.append( _raw( '2023-03-30', a, 1, b, 2 ))
            raws.append( _raw( '2023-03-31', b, 3, a, 4 ))
        parsed = ParsedGames( records=raws )
        clean  = TransformModel.convert( parsed )
        TransformModel.validateRoster( clean, requireMlbTeamCount=True )

    def test_raises_when_rosters_differ( self ):
        parsed = ParsedGames( records=[ _raw( '2023-03-30', 'A', 1, 'B', 2 ) ])
        clean  = TransformModel.convert( parsed )
        with self.assertRaises( ValueError ) as cm:
            TransformModel.validateRoster( clean, requireMlbTeamCount=False )
        self.assertIn( 'rosters differ', str( cm.exception ))

    def test_raises_when_team_count_is_wrong( self ):
        parsed = ParsedGames( records=_pair( 'A', 'B' ) )
        clean  = TransformModel.convert( parsed )
        with self.assertRaises( ValueError ) as cm:
            TransformModel.validateRoster( clean, requireMlbTeamCount=True )
        self.assertIn( 'expected 30', str( cm.exception ))

    def test_allows_small_roster_when_flag_disabled( self ):
        parsed = ParsedGames( records=_pair( 'A', 'B' ) )
        clean  = TransformModel.convert( parsed )
        TransformModel.validateRoster( clean, requireMlbTeamCount=False )


class TestRun( unittest.TestCase ):

    def test_run_raises_on_partial_data_by_default( self ):
        parsed = ParsedGames( records=_pair( 'A', 'B' ) )
        with self.assertRaises( ValueError ):
            TransformModel( parsed=parsed ).run()


if __name__ == '__main__':
    unittest.main()
