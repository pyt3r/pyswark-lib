import unittest

from pyswark.apps.baseball.steps.scrape import Scraped
from pyswark.apps.baseball.steps.parse  import ParseModel, ParsedGames, GAME_RE


class TestGameRegex( unittest.TestCase ):

    def test_matches_simple_game( self ):
        m = GAME_RE.match( 'Atlanta Braves (7) @ Washington Nationals (2)' )
        self.assertIsNotNone( m )
        self.assertEqual( m.group( 'awayTeam' ),  'Atlanta Braves' )
        self.assertEqual( m.group( 'awayScore' ), '7' )
        self.assertEqual( m.group( 'homeTeam' ),  'Washington Nationals' )
        self.assertEqual( m.group( 'homeScore' ), '2' )

    def test_matches_team_with_apostrophe( self ):
        m = GAME_RE.match( "Arizona D'Backs (10) @ St. Louis Cardinals (3)" )
        self.assertIsNotNone( m )
        self.assertEqual( m.group( 'awayTeam' ), "Arizona D'Backs" )
        self.assertEqual( m.group( 'homeTeam' ), 'St. Louis Cardinals' )

    def test_matches_multi_digit_scores( self ):
        m = GAME_RE.match( 'Team A (15) @ Team B (12)' )
        self.assertIsNotNone( m )
        self.assertEqual( m.group( 'awayScore' ), '15' )
        self.assertEqual( m.group( 'homeScore' ), '12' )

    def test_no_match_on_malformed_input( self ):
        self.assertIsNone( GAME_RE.match( 'not a game line' ))

    def test_matches_team_glued_to_parens_no_space( self ):
        # baseball-reference sometimes renders without a space between team
        # name and the score parens; trailing 'Boxscore' link text is OK
        # because GAME_RE is anchored only at the start.
        m = GAME_RE.match( 'Baltimore Orioles(10)@Boston Red Sox(9)Boxscore' )
        self.assertIsNotNone( m )
        self.assertEqual( m.group( 'awayTeam' ),  'Baltimore Orioles' )
        self.assertEqual( m.group( 'awayScore' ), '10' )
        self.assertEqual( m.group( 'homeTeam' ),  'Boston Red Sox' )
        self.assertEqual( m.group( 'homeScore' ), '9' )

    def test_matches_with_newline_between_score_and_at( self ):
        m = GAME_RE.match( 'Milwaukee Brewers(0)\n @Chicago Cubs(4)Boxscore' )
        self.assertIsNotNone( m )
        self.assertEqual( m.group( 'awayTeam' ),  'Milwaukee Brewers' )
        self.assertEqual( m.group( 'awayScore' ), '0' )
        self.assertEqual( m.group( 'homeTeam' ),  'Chicago Cubs' )
        self.assertEqual( m.group( 'homeScore' ), '4' )


class TestParse( unittest.TestCase ):

    def setUp( self ):
        self.scraped = Scraped(
            dates = [ 'Thursday, March 30, 2023', 'Thursday, March 30, 2023' ],
            games = [
                'Atlanta Braves (7) @ Washington Nationals (2)',
                'San Francisco Giants (5) @ New York Yankees (0)',
            ],
        )

    def test_parse_returns_one_record_per_game( self ):
        parsed = ParseModel.parse( self.scraped )
        self.assertIsInstance( parsed, ParsedGames )
        self.assertEqual( len( parsed.records ), 2 )

    def test_parse_preserves_date_and_splits_teams_and_scores( self ):
        parsed = ParseModel.parse( self.scraped )
        r0 = parsed.records[ 0 ]
        self.assertEqual( r0.date,      'Thursday, March 30, 2023' )
        self.assertEqual( r0.awayTeam,  'Atlanta Braves' )
        self.assertEqual( r0.awayScore, '7' )
        self.assertEqual( r0.homeTeam,  'Washington Nationals' )
        self.assertEqual( r0.homeScore, '2' )

    def test_parse_raises_on_unparseable_text( self ):
        bad = Scraped( dates=[ '2023-01-01' ], games=[ 'not a game' ])
        with self.assertRaises( ValueError ):
            ParseModel.parse( bad )

    def test_run_threads_scraped_through( self ):
        out = ParseModel( scraped=self.scraped ).run()
        self.assertIn( 'parsed', out )
        self.assertIsInstance( out[ 'parsed' ], ParsedGames )

    def test_toDataFrame_has_expected_columns( self ):
        parsed = ParseModel.parse( self.scraped )
        df = parsed.toDataFrame()
        self.assertListEqual(
            sorted( df.columns.tolist() ),
            sorted([ 'date', 'awayTeam', 'awayScore', 'homeTeam', 'homeScore' ]),
        )
        self.assertEqual( len( df ), 2 )


if __name__ == '__main__':
    unittest.main()
