"""Transform step: type-convert and validate the parsed games.

Input  : ``parsed`` — :class:`ParsedGames` of :class:`GameRaw` records (strings).
Output : ``clean``  — :class:`CleanGames` of :class:`Game` records with
         ``date : datetime``, ``awayScore/homeScore : int``.

Also validates that the home and away sides see the same roster, of exactly
``MLB_TEAM_COUNT`` teams. ``run()`` always enforces this for the full-season
workflow; unit tests that work on partial data should call the
:meth:`TransformModel.convert` and :meth:`TransformModel.validateRoster`
staticmethods directly (``validateRoster(clean, requireMlbTeamCount=False)``).
"""

from datetime import datetime
from typing import List

from dateutil import parser as dateparser

from pyswark.lib.pydantic import base
from pyswark.apps.baseball.steps.parse import GameRaw, ParsedGames


MLB_TEAM_COUNT = 30


class Game( base.BaseModel ):
    """One typed game record."""
    date      : datetime
    awayTeam  : str
    awayScore : int
    homeTeam  : str
    homeScore : int


class CleanGames( base.BaseModel ):
    """A list of typed :class:`Game` records with a ``toDataFrame()`` helper."""
    records : List[ Game ]

    def toDataFrame( self ):
        import pandas
        return pandas.DataFrame( r.model_dump() for r in self.records )


class TransformModel( base.BaseModel ):
    """Convert string fields to ints/datetimes and validate the roster."""

    parsed : ParsedGames

    def run( self ):
        clean = self.convert( self.parsed )
        self.validateRoster( clean, requireMlbTeamCount=True )
        return { 'clean': clean }

    @staticmethod
    def convert( parsed: ParsedGames ) -> CleanGames:
        return CleanGames( records=[ TransformModel._convertOne( r ) for r in parsed.records ])

    @staticmethod
    def _convertOne( raw: GameRaw ) -> Game:
        return Game(
            date      = dateparser.parse( raw.date ),
            awayTeam  = raw.awayTeam,
            awayScore = int( raw.awayScore ),
            homeTeam  = raw.homeTeam,
            homeScore = int( raw.homeScore ),
        )

    @staticmethod
    def validateRoster( clean: CleanGames, requireMlbTeamCount: bool = True ) -> None:
        away = sorted({ g.awayTeam for g in clean.records })
        home = sorted({ g.homeTeam for g in clean.records })

        if away != home:
            onlyAway = sorted( set( away ) - set( home ))
            onlyHome = sorted( set( home ) - set( away ))
            raise ValueError(
                f"home/away team rosters differ: "
                f"only-away={ onlyAway }, only-home={ onlyHome }"
            )

        if requireMlbTeamCount and len( away ) != MLB_TEAM_COUNT:
            raise ValueError(
                f"expected { MLB_TEAM_COUNT } teams, got { len( away ) }: { away }"
            )
