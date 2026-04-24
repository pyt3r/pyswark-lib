from pyswark.workflow.runner import Runner


def create( year: int ):
    """ Create a runner for the baseball ETL workflow.

    Parameters
    ----------
    year : int
        The year of the season to run the ETL workflow for.
    """

    return Runner(
        workflow =  'python://pyswark.apps.baseball.workflows.etl.WORKFLOW',
        state    = f'python://pyswark.apps.baseball.states.season.SEASON_{ year }',
    )
