import unittest
from unittest.mock import patch

from pyswark.apps.baseball.steps.scrape import ScrapeModel, Scraped


HTML = """
<html><body>
  <div class="section_content">
    <h3>Thursday, March 30, 2023</h3>
    <div>
      <p class="game">Atlanta Braves (7) @ Washington Nationals (2)</p>
      <p class="game">San Francisco Giants (5) @ New York Yankees (0)</p>
    </div>
    <h3>Friday, March 31, 2023</h3>
    <div>
      <p class="game">Chicago Cubs (3) @ Cincinnati Reds (4)</p>
    </div>
  </div>
</body></html>
"""


class TestScrape( unittest.TestCase ):

    def test_scrape_returns_parallel_lists( self ):
        scraped = ScrapeModel.scrape( HTML )
        self.assertIsInstance( scraped, Scraped )
        self.assertEqual( len( scraped.dates ), 3 )
        self.assertEqual( len( scraped.games ), 3 )

    def test_scrape_associates_date_with_each_game( self ):
        scraped = ScrapeModel.scrape( HTML )
        self.assertEqual( scraped.dates[0], 'Thursday, March 30, 2023' )
        self.assertEqual( scraped.dates[1], 'Thursday, March 30, 2023' )
        self.assertEqual( scraped.dates[2], 'Friday, March 31, 2023' )
        self.assertIn( 'Atlanta Braves', scraped.games[0] )
        self.assertIn( 'Chicago Cubs', scraped.games[2] )

    def test_scrape_missing_section_raises( self ):
        with self.assertRaises( ValueError ):
            ScrapeModel.scrape( '<html><body>nothing here</body></html>' )

    def test_run_reads_uri_and_delegates_to_scrape( self ):
        model = ScrapeModel( uri='file:./fake' )
        with patch( 'pyswark.apps.baseball.steps.scrape.io.read', return_value=HTML ):
            out = model.run()
        self.assertIn( 'scraped', out )
        self.assertIsInstance( out[ 'scraped' ], Scraped )
        self.assertEqual( len( out[ 'scraped' ].dates ), 3 )


if __name__ == '__main__':
    unittest.main()
