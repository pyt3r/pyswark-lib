from pyswark.apps.baseball.states import season

from pyswark.apps.baseball.runner.base import Runner


def create( year ):
    
    state = season.create( year )

    return Runner(
        workflow = 'python:pyswark.apps.baseball.workflows.etl.WORKFLOW',
        state    = state,
    )

