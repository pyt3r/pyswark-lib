from pyswark.workflow import state


def create( year: int ):
    """Create initial state for a season ETL run.

    Parameters
    ----------
    uri : str
        URI pointing to the season schedule data source.
    """

    uri = f"gdrive2://@phb2114/baseball/{ year }-schedule.shtml"
    # uri = f'https://www.baseball-reference.com/leagues/MLB/{ year }-schedule.shtml'
    
    return state.StateWithGlueDb( backend={ 'uri': uri } )


SEASON_2023 = create( 2023 )
