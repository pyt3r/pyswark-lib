from pyswark.workflow.workflow import Workflow
from pyswark.workflow.step import Step


WORKFLOW = Workflow(
    steps=[
        Step(
            model   = 'pyswark.apps.baseball.steps.scrape.ScrapeModel',
            inputs  = { 'uri': 'uri' },
            outputs = { 'scraped': 'scraped' },
        ),
        Step(
            model   = 'pyswark.apps.baseball.steps.parse.ParseModel',
            inputs  = { 'scraped': 'scraped' },
            outputs = { 'parsed': 'parsed' },
        ),
        Step(
            model   = 'pyswark.apps.baseball.steps.transform.TransformModel',
            inputs  = { 'parsed': 'parsed' },
            outputs = { 'clean': 'clean' },
        ),
    ],
)
