import unittest

from pyswark.lib.pydantic import base, ser_des
from pyswark.workflow.state import Interface, State, StateWithGlueDb
from pyswark.workflow.step import Step
from pyswark.workflow.workflow import Workflow
from pyswark.workflow.runner import Runner


class AddModel( base.BaseModel ):
    a: int
    b: int

    def run( self ):
        return { 'c' : self.a + self.b }


WORKFLOW_FOR_URI_TEST = Workflow(
    steps=[
        Step(
            model   = AddModel,
            inputs  = { 'external.a': 'a', 'external.b': 'b' },
            outputs = { 'c': 'external.c' },
        ),
    ],
)


STATE_FOR_URI_TEST = State( backend={ 'external.a': 10, 'external.b': 20 } )


class RunnerMixin:
    STATE_CLASS = None  # State or StateWithGlueDb

    def _makeWorkflow( self ):
        return Workflow(
            steps=[
                Step(
                    model   = AddModel,
                    inputs  = { 'external.a': 'a', 'external.b': 'b' },
                    outputs = { 'c': 'external.c' },
                ),
            ],
        )

    def _makeState( self ):
        return self.STATE_CLASS( backend={ 'external.a': 1, 'external.b': 2 } )

    def _makeRunner( self ):
        return Runner( workflow=self._makeWorkflow(), state=self._makeState() )

    def test_run_returns_final_output( self ):
        runner = self._makeRunner()
        result = runner.run()
        self.assertEqual( result, { 'external.c': 3 } )

    def test_run_caches_workflow_and_state( self ):
        runner = self._makeRunner()
        self.assertIsNone( runner.rerunWorkflow )
        self.assertIsNone( runner.rerunState )

        runner.run()

        self.assertIsInstance( runner.rerunWorkflow, Workflow )
        self.assertIsInstance( runner.rerunState, Interface )
        self.assertListEqual( runner.rerunWorkflow.stepsRan, [0] )
        self.assertListEqual( runner.rerunWorkflow.stepsSkipped, [] )
        self.assertEqual( runner.rerunState.extract('external.c'), 3 )

    def test_rerun_skips_steps_and_returns_same_output( self ):
        runner = self._makeRunner()
        first = runner.run()
        second = runner.rerun()

        self.assertEqual( first, second )
        self.assertEqual( second, { 'external.c': 3 } )
        self.assertListEqual( runner.rerunWorkflow.stepsRan, [0] )
        self.assertListEqual( runner.rerunWorkflow.stepsSkipped, [0] )

    def test_rerun_before_run_raises( self ):
        runner = self._makeRunner()
        with self.assertRaises( ValueError ):
            runner.rerun()

    def test_getRerunWorkflow_applies_flags( self ):
        runner = self._makeRunner()
        runner.run()

        workflow = runner.getRerunWorkflow( useExtracts=False, populateExtracts=False )
        self.assertIs( workflow, runner.rerunWorkflow )
        self.assertFalse( workflow.useExtracts )
        self.assertFalse( workflow.populateExtracts )

        workflow = runner.getRerunWorkflow( useExtracts=True )
        self.assertTrue( workflow.useExtracts )
        self.assertFalse( workflow.populateExtracts )  # unchanged

    def test_getRerunWorkflow_without_run_raises( self ):
        runner = self._makeRunner()
        with self.assertRaises( ValueError ):
            runner.getRerunWorkflow()

    def test_getRerunState_without_run_raises( self ):
        runner = self._makeRunner()
        with self.assertRaises( ValueError ):
            runner.getRerunState()


class TestRunnerWithState( RunnerMixin, unittest.TestCase ):
    STATE_CLASS = State


class TestRunnerWithStateWithGlueDb( RunnerMixin, unittest.TestCase ):
    STATE_CLASS = StateWithGlueDb


class TestRunnerResolvesStringRefs( unittest.TestCase ):
    """String workflow/state refs are resolved via pyswark.core.io (python://)."""

    URI_WORKFLOW = 'python://pyswark.tests.unittests.workflow.test_runner.WORKFLOW_FOR_URI_TEST'
    URI_STATE    = 'python://pyswark.tests.unittests.workflow.test_runner.STATE_FOR_URI_TEST'

    def test_run_resolves_string_refs( self ):
        runner = Runner( workflow=self.URI_WORKFLOW, state=self.URI_STATE )
        result = runner.run()

        self.assertEqual( result, { 'external.c': 30 } )
        self.assertIsInstance( runner.rerunWorkflow, Workflow )
        self.assertIsInstance( runner.rerunState, Interface )
        self.assertListEqual( runner.rerunWorkflow.stepsRan, [0] )
        self.assertEqual( runner.rerunState.extract('external.c'), 30 )

    def test_getWorkflow_returns_instance_unchanged( self ):
        workflow = WORKFLOW_FOR_URI_TEST
        state    = State( backend={ 'external.a': 1, 'external.b': 2 } )
        runner   = Runner( workflow=workflow, state=state )
        self.assertIs( runner.getWorkflow(), workflow )
        self.assertIs( runner.getState(), state )


class TestRunnerSerDes( unittest.TestCase ):

    def test_ser_des_with_string_refs( self ):
        runner = Runner(
            workflow = 'python://pyswark.tests.unittests.workflow.test_runner.WORKFLOW_FOR_URI_TEST',
            state    = 'python://pyswark.tests.unittests.workflow.test_runner.STATE_FOR_URI_TEST',
        )
        ser = runner.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( des, runner )
