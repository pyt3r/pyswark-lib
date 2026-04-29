"""
Workflow Runner
===============

This module provides the :class:`Runner` class, a thin convenience wrapper
that assembles and executes a :class:`~pyswark.workflow.workflow.Workflow`
against a :class:`~pyswark.workflow.state.Interface` (state) object.

A ``Runner`` accepts the workflow and state either as instances or as
URI-addressable references (strings resolved via
:func:`pyswark.core.io.api.read`, typically ``python://`` URIs). After
running, the post-run workflow and state are cached on the runner so the
caller can inspect intermediate extracts or rerun.

Example
-------
>>> from pyswark.workflow.runner import Runner
>>> runner = Runner( workflow=my_workflow, state=my_state )
>>> result = runner.run()
>>> result2 = runner.rerun()   # reruns using the cached workflow/state
"""

from typing import Union

from pyswark.lib.pydantic import base
from pyswark.core.io import api as io

from pyswark.workflow.state import Interface
from pyswark.workflow.workflow import Workflow


class Runner( base.BaseModel ):
    """Assembles and runs a workflow with a dynamically resolved state."""

    workflow : Union[ str, Workflow ]
    state    : Union[ str, Interface ]

    rerunWorkflow  : Union[ None, Workflow ]  = None
    rerunState     : Union[ None, Interface ] = None

    def run( self ):
        workflow = self.getWorkflow()
        state    = self.getState()

        self.rerunWorkflow = workflow
        self.rerunState    = state

        results  = workflow.run( state )

        return results

    def getWorkflow( self ):
        return io.read( self.workflow ) if isinstance( self.workflow, str ) else self.workflow

    def getState( self ):
        return io.read( self.state ) if isinstance( self.state, str ) else self.state


    def rerun( self, **kw ):
        workflow = self.getRerunWorkflow(**kw)
        state    = self.getRerunState()

        runner  = Runner( workflow=workflow, state=state )
        results = runner.run()

        self.rerunWorkflow = runner.rerunWorkflow
        self.rerunState    = runner.rerunState

        return results

    def getRerunState( self ):
        state = self.rerunState

        if state is None:
            raise ValueError( "Cannot rerun workflow without a rerunState" )

        return state

    def getRerunWorkflow( self, useExtracts=None, populateExtracts=None ):
        workflow = self.rerunWorkflow

        if workflow is None:
            raise ValueError( "Cannot rerun workflow without a rerunWorkflow" )

        useExtracts      = useExtracts if useExtracts is not None else workflow.useExtracts
        populateExtracts = populateExtracts if populateExtracts is not None else workflow.populateExtracts

        workflow.useExtracts = useExtracts
        workflow.populateExtracts = populateExtracts

        return workflow
