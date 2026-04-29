"""Scrape step: read a baseball-reference schedule page and extract raw game text.

Input  : ``uri`` pointing at an HTML schedule page (e.g., a local gdrive2 copy
         of ``YYYY-schedule.shtml`` or the live baseball-reference URL).
Output : ``scraped`` — a parallel-list dict ``{'dates': [...], 'games': [...]}``
         where ``dates[i]`` is the date header string for the i-th game text
         and ``games[i]`` is the raw un-parsed game text
         (e.g., ``"Atlanta Braves (7) @ Washington Nationals (2)"``).

Downstream steps (not yet implemented) are responsible for regex-parsing each
game string into typed fields and type-converting the dates.
"""

from typing import List

from bs4 import BeautifulSoup

from pyswark.lib.pydantic import base
from pyswark.core.io import api as io


SECTION_CLASS = 'section_content'
GAME_CLASS    = 'game'


class Scraped( base.BaseModel ):
    """Raw scraped output: parallel lists of per-game date and text."""
    dates : List[ str ]
    games : List[ str ]


class ScrapeModel( base.BaseModel ):
    """Scrape a baseball-reference schedule page into raw per-game text."""

    uri: str

    def run( self ):
        html    = io.read( self.uri )
        scraped = self.scrape( html )
        return { 'scraped': scraped }

    @staticmethod
    def scrape( html: str ) -> Scraped:
        
        doc     = BeautifulSoup( html, 'html.parser' )
        section = doc.find( class_=SECTION_CLASS )
        if section is None:
            raise ValueError( f"no element with class={ SECTION_CLASS !r} found" )

        headers  = section.find_all( 'h3' )
        gamedays = section.find_all( 'div' )
        if len( headers ) != len( gamedays ):
            raise ValueError(
                f"header/gameday mismatch: { len(headers) } headers vs "
                f"{ len(gamedays) } gamedays"
            )

        dates: List[ str ] = []
        games: List[ str ] = []
        for header, gameday in zip( headers, gamedays ):
            for game in gameday.find_all( class_=GAME_CLASS ):
                dates.append( header.get_text( strip=True ) )
                games.append( game.get_text( strip=True ) )

        return Scraped( dates=dates, games=games )
