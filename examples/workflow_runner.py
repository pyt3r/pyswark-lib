"""
Workflow Runner
===============

The :class:`~pyswark.workflow.runner.Runner` assembles a
:class:`~pyswark.workflow.workflow.Workflow` and a
:class:`~pyswark.workflow.state.State`, runs them, and caches the post-run
artifacts for inspection and rerunning. Runners are the stable public entry
point for every application under ``pyswark.apps``.

This example walks through the runner end-to-end with a tiny two-step
arithmetic workflow: ``(x + y) * k``.
"""

# %%
# Define the step models — the actual compute. In a real application these
# would live one-per-file under ``pyswark/apps/<name>/steps/``.

from pyswark.lib.pydantic import base


class AddModel( base.BaseModel ):
    a: int
    b: int

    def run( self ):
        return { 'sum': self.a + self.b }


class MultiplyModel( base.BaseModel ):
    value  : int
    factor : int

    def run( self ):
        return { 'product': self.value * self.factor }


# %%
# Compose the step models into a ``Workflow``. Each ``Step`` wires a model's
# fields to/from named slots in the shared state:
#
# * ``inputs``: ``{state_name: model_field_name}``
# * ``outputs``: ``{model_output_key: state_name}``
#
# In a real application this module-level ``WORKFLOW`` would live under
# ``pyswark/apps/<name>/workflows/<graph>.py``.

from pyswark.workflow.workflow import Workflow
from pyswark.workflow.step import Step

WORKFLOW = Workflow( steps=[
    Step(
        model   = AddModel,
        inputs  = { 'x': 'a', 'y': 'b' },
        outputs = { 'sum': 'total' },
    ),
    Step(
        model   = MultiplyModel,
        inputs  = { 'total': 'value', 'k': 'factor' },
        outputs = { 'product': 'final' },
    ),
])


# %%
# Build an initial state. A state factory like this would typically live under
# ``pyswark/apps/<name>/states/<scenario>.py``.

from pyswark.workflow.state import State


def make_state():
    return State( backend={ 'x': 2, 'y': 3, 'k': 4 } )


# %%
# Wire a ``Workflow`` and ``State`` into a ``Runner`` and run it.

from pyswark.workflow.runner import Runner

runner = Runner( workflow=WORKFLOW, state=make_state() )
result = runner.run()
print( "result:", result )    # {'final': 20}  —  (2 + 3) * 4


# %%
# After ``run()``, the post-run workflow and state are stashed on the runner
# as ``rerunWorkflow`` / ``rerunState`` so you can inspect what happened.

wf = runner.rerunWorkflow
print( "stepsRan:    ", wf.stepsRan )       # [0, 1]
print( "stepsSkipped:", wf.stepsSkipped )   # []

print( "state['total']:", runner.rerunState.extract('total') )
print( "state['final']:", runner.rerunState.extract('final') )

print( "cached input for step 0:",  wf.getModelInput(0) )
print( "cached output for step 0:", wf.getModelOutput(0) )


# %%
# ``rerun()`` replays the workflow against the cached state. Because the
# inputs are unchanged, every step is skipped — the cache makes reruns cheap
# and idempotent on immutable state. Note that ``stepsRan`` and
# ``stepsSkipped`` **accumulate** across runs (they are not reset).

result2 = runner.rerun()
print( "rerun result:", result2 )                          # {'final': 20}
print( "stepsRan:    ", runner.rerunWorkflow.stepsRan )     # [0, 1]
print( "stepsSkipped:", runner.rerunWorkflow.stepsSkipped ) # [0, 1]


# %%
# You can override the caching flags on ``rerun()`` to force a full
# re-execution.  Pairing ``useExtracts=False`` with ``populateExtracts=False``
# runs every step from scratch without updating the cache.  Because state is
# immutable by default, this works here only because the workflow's
# idempotent post rule avoids re-writing unchanged output names on the
# skipped path; a fresh run on an already-populated immutable state will
# fail on write. In production, pass a fresh state factory (or a
# ``StateWithGlueDb`` with ``mutable=True``) when forcing re-execution.

# %%
# **String refs for production.**  In real applications, pass ``workflow``
# and ``state`` as ``python://module.path`` reference strings. The ``Runner``
# resolves them lazily via :func:`pyswark.core.io.api.read`, which
# re-imports the target module on every ``run()`` — each call gets a fresh
# instance, and the runner itself serializes cleanly:
#
# .. code-block:: python
#
#    from pyswark.workflow.runner import Runner
#
#    runner = Runner(
#        workflow = 'python://mypkg.apps.<name>.workflows.etl.WORKFLOW',
#        state    = 'python://mypkg.apps.<name>.states.season.SEASON_2023',
#    )
#    result = runner.run()
