import unittest
import tempfile
from pathlib import Path

from pyswark.workflow.runner import Runner
from pyswark.workflow.state  import State
from pyswark.apps.baseball.steps.transform import CleanGames


def _buildHtml( teams ):
    """Build a synthetic schedule page with a home/away pair per team."""
    rows = []
    for i, a in enumerate( teams ):
        b = teams[ ( i + 1 ) % len( teams ) ]
        rows.append( f'<p class="game">{ a } (1) @ { b } (2)</p>' )
        rows.append( f'<p class="game">{ b } (3) @ { a } (4)</p>' )
    games = '\n'.join( rows )
    return (
        '<html><body>'
        '<div class="section_content">'
        '<h3>Thursday, March 30, 2023</h3>'
        f'<div>{ games }</div>'
        '</div>'
        '</body></html>'
    )


def _htmlFixtureUri( html: str, tmpdir: Path ) -> str:
    """Write html to a tmp file and return its ``file:`` URI for io.read."""
    fp = tmpdir / 'schedule.shtml'
    fp.write_text( html )
    return f'file:{ fp }'


def _runner( state: State ) -> Runner:
    """Runner pointing at the real WORKFLOW (via python:// so each run
    reimports it fresh) and an inline state — no dedicated state factory
    module is needed for tests."""
    return Runner(
        workflow = 'python://pyswark.apps.baseball.workflows.etl.WORKFLOW',
        state    = state,
    )


class TestEtlWorkflow( unittest.TestCase ):

    def setUp( self ):
        self._tmpdir_ctx = tempfile.TemporaryDirectory()
        self.tmpdir      = Path( self._tmpdir_ctx.name )
        self.teams       = [ f'Team{ i }' for i in range( 30 ) ]
        self.uri         = _htmlFixtureUri( _buildHtml( self.teams ), self.tmpdir )

    def tearDown( self ):
        self._tmpdir_ctx.cleanup()

    def test_runs_all_three_steps_and_posts_clean_to_state( self ):
        state  = State({ 'uri': self.uri })
        runner = _runner( state )
        runner.run()

        self.assertListEqual( runner.rerunWorkflow.stepsRan,     [ 0, 1, 2 ] )
        self.assertListEqual( runner.rerunWorkflow.stepsSkipped, [] )

        for name in ( 'scraped', 'parsed', 'clean' ):
            self.assertIn( name, state.backend )

        clean = state.extract( 'clean' )
        self.assertIsInstance( clean, CleanGames )
        self.assertEqual( len( clean.records ), 2 * len( self.teams ))

    def test_rerun_skips_all_cached_steps( self ):
        state  = State({ 'uri': self.uri })
        runner = _runner( state )
        runner.run()
        runner.rerun()

        self.assertListEqual( runner.rerunWorkflow.stepsRan,     [ 0, 1, 2 ] )
        self.assertListEqual( runner.rerunWorkflow.stepsSkipped, [ 0, 1, 2 ] )

    def test_validation_fails_on_rosters_with_fewer_than_30_teams( self ):
        uri    = _htmlFixtureUri( _buildHtml([ 'OnlyA', 'OnlyB' ]), self.tmpdir )
        state  = State({ 'uri': uri })
        runner = _runner( state )

        with self.assertRaises( ValueError ):
            runner.run()


if __name__ == '__main__':
    unittest.main()
