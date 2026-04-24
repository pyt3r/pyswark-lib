from pyswark.workflow.state import StateWithGlueDb


def create( uri ):
    """Create initial state for a season ETL run.

    Parameters
    ----------
    uri : str
        URI pointing to the season schedule data source.
    """
    return StateWithGlueDb( backend={ 'uri': uri } )
