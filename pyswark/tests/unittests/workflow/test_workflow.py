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
        return { 'internal.c' : result }


class AnotherExampleModel( base.BaseModel ):
    a: int
    b: int
    c: int

    def run( self ):
        result = self.a + self.b + self.c
        return { 'internal.d' : result }


class TestStep( unittest.TestCase ):

    def setUp( self ):
        self.stateData = { 'external.a': 1, 'external.b': 2 }

        self.step1 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'internal.c' : 'external.c'
            },
        )

    def test_running_a_step( self ):
        state  = State( self.stateData )
        step1  = self.step1
        result = step1.run( state )

        self.assertDictEqual( result, { 'external.c': 3 } )
        self.assertEqual( state.extract('external.c'), 3 )

    def test_ser_des(self):
        step1 = self.step1
        ser = step1.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( des, step1 )
        

class TestStepImmutability( unittest.TestCase ):

    def setUp( self ):
        self.step1 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'internal.c' : 'external.a'
            },
        )
        self.stateData = { 'external.a': 1, 'external.b': 2 }

    def test_running_a_step_with_mutable_state( self ):
        state  = State( self.stateData, mutable=True )
        step1  = self.step1
        result = step1.run( state )

        self.assertDictEqual( result, { 'external.a': 3 } )
        self.assertEqual( state.extract('external.a'), 3 )

    def test_running_a_step_with_immutable_state( self ):
        step1 = self.step1
        state = state = State( self.stateData, mutable=False )

        with self.assertRaises( ValueError ):
            step1.run( state )


class TestWorkflow( unittest.TestCase ):

    def setUp( self ):
        self.state = State({ 'external.a': 1, 'external.b': 2 })

        step1 = Step( 
            model = ExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
            },
            outputs={
                'internal.c' : 'external.c'
            },
        )
        self.workflow = Workflow( steps=[step1] )

        self.step2 = Step( 
            model = AnotherExampleModel, 
            inputs = {
                'external.a': 'a',
                'external.b': 'b',
                'external.c': 'c',
            },
            outputs={
                'internal.d' : 'external.d'
            },
        )

    def test_workflow_with_one_step( self ):
        workflow = self.workflow
        result = workflow.run( self.state )
        self.assertEqual( result, { 'external.c': 3 } )
        self.assertEqual( self.state.extract('external.c'), 3 )
        
    def test_workflow_with_two_steps( self ):
        workflow = self.workflow
        workflow.addStep( self.step2 )
        result = workflow.run( self.state )
        self.assertEqual( result, { 'external.d': 6 } )
        self.assertEqual( self.state.extract('external.d'), 6 )
        
    def test_ser_des(self):
        workflow = self.workflow
        workflow.addStep( self.step2 )
        ser = workflow.toJson()
        des = ser_des.fromJson( ser )
        self.assertEqual( des, workflow )
        