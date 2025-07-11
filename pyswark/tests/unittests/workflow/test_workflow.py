import unittest

from pyswark.lib.pydantic import base, ser_des
from pyswark.workflow.workflow import Workflow
from pyswark.workflow.step import Step
from pyswark.workflow.state import State


class ExampleModel( base.BaseModel ):
    a: int
    b: int

    def run( self ):
        result = self.a + self.b
        return { 'c' : result }

class AnotherExampleModel( base.BaseModel ):
    b: int
    c: int

    def run( self ):
        result = self.b + self.c
        return { 'd' : result }

class OneMoreExampleModel( base.BaseModel ):
    a: int
    d: int

    def run( self ):
        result = self.a + self.d
        return { 'e' : result }


class TestStep( unittest.TestCase ):

    def setUp( self ):
        self.stateData = { 'external.a': 1, 'external.b': 2 }

        self.step0 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'c' : 'external.c'
            },
        )

    def test_running_a_step( self ):
        state  = State( self.stateData )
        step0  = self.step0
        result = step0.run( state )

        self.assertDictEqual( result, { 'external.c': 3 } )
        self.assertEqual( state.extract('external.c'), 3 )

    def test_ser_des(self):
        step0 = self.step0
        ser = step0.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( des, step0 )
        

class TestStepImmutability( unittest.TestCase ):

    def setUp( self ):
        self.step0 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'c' : 'external.a'
            },
        )
        self.stateData = { 'external.a': 1, 'external.b': 2 }

    def test_running_a_step_with_mutable_state( self ):
        state  = State( self.stateData, mutable=True )
        step0  = self.step0
        result = step0.run( state )

        self.assertDictEqual( result, { 'external.a': 3 } )
        self.assertEqual( state.extract('external.a'), 3 )

    def test_running_a_step_with_immutable_state( self ):
        step0 = self.step0
        state = state = State( self.stateData, mutable=False )

        with self.assertRaises( ValueError ):
            step0.run( state )


class TestWorkflow( unittest.TestCase ):

    def setUp( self ):
        self.state = State({ 'external.a': 1, 'external.b': 2 })

        step0 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'c' : 'external.c'
            },
        )
        self.workflow = Workflow( steps=[step0] )

        self.step1 = Step( 
            model = AnotherExampleModel, 
            inputs = {
                'external.b': 'b',
                'external.c': 'c',
            },
            outputs={
                'd' : 'external.d'
            },
        )

        self.step2 = Step( 
            model = OneMoreExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.d': 'd',
            },
            outputs={
                'e' : 'external.e'
            },
        )
    def test_workflow_with_one_step( self ):
        workflow = self.workflow
        result = workflow.run( self.state )
        self.assertEqual( result, { 'external.c': 3 } )
        self.assertEqual( self.state.extract('external.c'), 3 )
        self.assertListEqual( workflow.stepsSkipped, [] )
        self.assertListEqual( workflow.stepsRan, [0] )

        self.assertEqual( workflow.getModelInput(0), { 'a': 1, 'b': 2 } )
        self.assertEqual( workflow.getModelOutput(0), { 'c': 3 } )
        
        model = workflow.getModel(0)
        self.assertEqual( model.a, 1 )
        self.assertEqual( model.b, 2 )
        self.assertEqual( model.run(), { 'c': 3 } )
        
    def test_workflow_with_two_steps( self ):
        workflow = self.workflow
        workflow.addStep( self.step1 )
        result = workflow.run( self.state )
        self.assertEqual( result, { 'external.d': 5 } )
        self.assertEqual( self.state.extract('external.d'), 5 )
        self.assertListEqual( workflow.stepsSkipped, [] )
        self.assertListEqual( workflow.stepsRan, [0, 1] )    

    def test_workflow_with_three_steps( self ):
        workflow = self.workflow
        workflow.addStep( self.step1 )
        workflow.addStep( self.step2 )
        result = workflow.run( self.state )
        self.assertEqual( result, { 'external.e': 6 } )
        self.assertListEqual( workflow.stepsSkipped, [] )
        self.assertListEqual( workflow.stepsRan, [0, 1, 2] )

    def test_ser_des(self):
        workflow = self.workflow
        workflow.addStep( self.step1 )
        ser = workflow.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( des, workflow )
        

class TestWorkflowWithExtracts( unittest.TestCase ):

    def setUp( self ):
        self.state = State({ 'external.a': 1, 'external.b': 2 })

        step0 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'c' : 'external.c'
            },
        )
        self.workflow = Workflow(
            steps=[step0],
            inputs={
                # 0: {'a': 1, 'b': 2},  # do not skip
                1: {'b': 2, 'c': 3},
                2: {'a': 1, 'd': 5},
            },
            outputs={
                0: {'c': 3}, 
                1: {'d': 5}, 
                # 2: {'e': 6}, # do not skip
            },
        )

        self.step1 = Step( 
            model = AnotherExampleModel, 
            inputs = {
                'external.b': 'b',
                'external.c': 'c',
            },
            outputs={
                'd' : 'external.d'
            },
        )

        self.step2 = Step( 
            model = OneMoreExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.d': 'd',
            },
            outputs={
                'e' : 'external.e'
            },
        )
    
    def test_three_step_workflow_with_extracts( self ):
        workflow = self.workflow
        workflow.addStep( self.step1 )
        workflow.addStep( self.step2 )
        result = workflow.run( self.state )
        self.assertEqual( result, { 'external.e': 6 } )
        self.assertListEqual( workflow.stepsSkipped, [1] )
        self.assertListEqual( workflow.stepsRan, [0, 2] )

        self.assertEqual( workflow.getModelOutput(1), {'d': 5} )
        self.assertEqual( workflow.getModelOutput(2), {'e': 6} )
