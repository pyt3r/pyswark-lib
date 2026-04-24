from pyswark.workflow.workflow import Workflow
from pyswark.workflow.step import Step


def create():
    """Create the baseball ETL workflow."""
    return Workflow(
        steps=[
            Step(
                model   = 'pyswark.apps.baseball.steps.extract.ExtractModel',
                inputs  = { 'uri': 'uri' },
                outputs = { 'data': 'raw_data' },
            ),
        ],
    )
