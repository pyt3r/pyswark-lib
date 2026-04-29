"""Parse step: regex the scraped game text into structured (but untyped) records.

Input  : ``scraped`` — :class:`Scraped` from the scrape step.
Output : ``parsed``  — :class:`ParsedGames` wrapping a list of
         :class:`GameRaw` records with all fields as raw strings. Downstream
         ``transform`` step is responsible for type conversion and validation.

Why a pydantic wrapper and not a ``pandas.DataFrame``?
-----------------------------------------------------
``Workflow._skipModel`` compares cached vs current model inputs with ``==`` —
on a ``DataFrame`` that returns an element-wise boolean frame rather than a
scalar ``bool``, which breaks the skip/rerun invariant. ``StateWithGlueDb``
also can't auto-``Infer`` a ``DataFrame``. A typed pydantic wrapper gives
clean equality, gluedb round-trips, *and* a ``toDataFrame()`` shortcut when a
consumer actually wants tabular analysis.
"""

import re
from typing import List

from pyswark.lib.pydantic import base
from pyswark.apps.baseball.steps.scrape import Scraped


def _teamScore( key: str ) -> str:
    """Named captures for one side: ``{key}Team`` and ``{key}Score``.

    The separator between team and ``(score)`` is ``\\s*`` (not ``\\s+``) because
    baseball-reference's rendered HTML sometimes glues them together
    (``Baltimore Orioles(10)``) and sometimes spaces them out
    (``Atlanta Braves (7)``). Both forms must parse.
    """
    team  = rf'(?P<{ key }Team>\S[\S\s]+?\S)'
    score = rf'\((?P<{ key }Score>\d+)\)'
    return rf'{ team }\s*{ score }'


def _gamePattern( away: str = 'away', home: str = 'home' ) -> str:
    """Full pattern: ``Away Name (X) @ Home Name (Y)``."""
    return rf'\s*{ _teamScore( away ) }\s*@\s*{ _teamScore( home ) }\s*'


GAME_RE = re.compile( _gamePattern() )


class GameRaw( base.BaseModel ):
    """One parsed game, all fields as raw strings (pre-type-conversion)."""
    date      : str
    awayTeam  : str
    awayScore : str
    homeTeam  : str
    homeScore : str


class ParsedGames( base.BaseModel ):
    """A list of :class:`GameRaw` records with a ``toDataFrame()`` helper."""
    records : List[ GameRaw ]

    def toDataFrame( self ):
        import pandas
        return pandas.DataFrame( r.model_dump() for r in self.records )


class ParseModel( base.BaseModel ):
    """Apply :data:`GAME_RE` to each scraped game text, producing raw records."""

    scraped: Scraped

    def run( self ):
        return { 'parsed': self.parse( self.scraped ) }

    @staticmethod
    def parse( scraped: Scraped ) -> ParsedGames:

        errors : List[ str ]     = []
        records: List[ GameRaw ] = []

        for i, ( date, text ) in enumerate( zip( scraped.dates, scraped.games )):
            match = GAME_RE.match( text )
            if match is None:
                errors.append( f"[{ i }] unparseable: { text !r}" )
                continue
            records.append( GameRaw( date=date, **match.groupdict() ))

        if errors:
            raise ValueError( "parse errors:\n  " + "\n  ".join( errors ))

        return ParsedGames( records=records )
