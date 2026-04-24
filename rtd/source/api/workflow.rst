workflow - Orchestration
========================

The ``workflow`` module provides orchestration of multi-step computations
with caching and reproducibility. This is Layer 2 of the architecture.

Key Concepts
------------

- **Step**: A single unit of work that wires a compute model's fields to/from named state slots.
- **Workflow**: An ordered list of ``Step`` instances with input/output caching (``modelInputs`` / ``modelOutputs``).
- **State**: A shared, named key-value store passed between steps. Two backends: ``State`` (plain dict) and ``StateWithGlueDb`` (SQLite-backed via GlueDb).
- **Runner**: A thin wrapper that assembles a ``Workflow`` and ``State`` (as instances or ``python://`` refs) and runs them.

Workflow Class
--------------

.. automodule:: pyswark.workflow.workflow
   :members: Workflow, Extracts
   :undoc-members:
   :show-inheritance:

Step Class
----------

.. automodule:: pyswark.workflow.step
   :members: Step
   :undoc-members:
   :show-inheritance:

State Classes
-------------

.. automodule:: pyswark.workflow.state
   :members: Interface, State, StateWithGlueDb
   :undoc-members:
   :show-inheritance:

Runner Class
------------

.. automodule:: pyswark.workflow.runner
   :members: Runner
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Workflow
^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.workflow.workflow import Workflow
   from pyswark.workflow.step import Step
   from pyswark.workflow.state import State

   workflow = Workflow(steps=[
       Step(
           model='mymodule.PreprocessModel',
           inputs={'raw_data': 'data'},      # state 'raw_data' -> model field 'data'
           outputs={'processed': 'clean'},   # model output 'processed' -> state 'clean'
       ),
       Step(
           model='mymodule.AnalysisModel',
           inputs={'clean': 'data'},
           outputs={'result': 'analysis'},
       ),
   ])

   # Initialize state with input data. State.post signature is post(data, name=...)
   state = State()
   state.post(my_dataframe, name='raw_data')

   result = workflow.run(state)

Workflow with Caching
^^^^^^^^^^^^^^^^^^^^^

Workflows cache each step's inputs and outputs in ``modelInputs`` and
``modelOutputs``. On subsequent runs, any step whose current input matches
its cached input is skipped and its cached output is used instead.

.. code-block:: python

   # First run — all steps execute
   result1 = workflow.run(state)
   print(workflow.stepsRan)      # [0, 1]
   print(workflow.stepsSkipped)  # []

   # Second run — steps are skipped if inputs are unchanged.
   # Note: stepsRan and stepsSkipped accumulate across runs; they are not reset.
   result2 = workflow.run(state)
   print(workflow.stepsRan)      # [0, 1]  — still from first run
   print(workflow.stepsSkipped)  # [0, 1]  — newly skipped on the second run

On a skipped step, the workflow posts cached outputs to state only for names
that are not already present. This makes ``workflow.run(state)`` safely
re-callable against immutable ``StateWithGlueDb`` backends.

Toggle caching with the ``useExtracts`` and ``populateExtracts`` flags on
``Workflow``:

.. code-block:: python

   workflow.useExtracts = False        # do not consult the cache; always run
   workflow.populateExtracts = False   # do not update the cache after each step

Creating a Model for Workflow Steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Models used in workflows are Pydantic models (extending
``pyswark.lib.pydantic.base.BaseModel``) with a ``run()`` method that returns
a dict:

.. code-block:: python

   from pyswark.lib.pydantic import base
   from pyswark.core.io import api as io

   class ExtractModel(base.BaseModel):
       uri: str

       def run(self):
           return {'data': io.read(self.uri)}

   class TransformModel(base.BaseModel):
       data: object

       def run(self):
           return {'processed': self.data.dropna()}

The ``Step`` then references the model by class (or fully-qualified string
path) and maps the state ↔ model field names:

.. code-block:: python

   from pyswark.workflow.step import Step

   extract  = Step(model=ExtractModel,
                   inputs={'uri': 'uri'},
                   outputs={'data': 'raw'})
   transform = Step(model=TransformModel,
                    inputs={'raw': 'data'},
                    outputs={'processed': 'clean'})

Inspecting Workflow State
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Cached inputs/outputs per step index
   model_input  = workflow.getModelInput(0)
   model_output = workflow.getModelOutput(0)

   # Reconstruct the model instance used at step 0
   model = workflow.getModel(0)

Runner: the top-level entry point
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Runner`` is a thin wrapper that assembles a ``Workflow`` and a ``State``
and runs them. Both may be passed as instances or as ``python://module.path``
reference strings; strings are resolved lazily via
:func:`pyswark.core.io.api.read` on every call (``reloadmodule=True`` by
default), which gives you a fresh instance on each ``run()``.

.. code-block:: python

   from pyswark.workflow.runner import Runner

   runner = Runner(
       workflow = 'python://mymodule.workflows.etl.WORKFLOW',
       state    = 'python://mymodule.states.season.SEASON_2023',
   )
   result = runner.run()

   # Post-run workflow and state are cached on the runner for inspection
   print(runner.rerunWorkflow.stepsRan)
   print(runner.rerunState.extract('clean'))

   # `rerun()` replays the workflow against the cached state. Same inputs ->
   # all steps are skipped. Pass flag overrides to force re-execution.
   result = runner.rerun()
   result = runner.rerun(useExtracts=False, populateExtracts=False)

See the :doc:`/examples/workflow_runner` gallery example for an end-to-end
walkthrough.

Application layout
^^^^^^^^^^^^^^^^^^

Applications that use the workflow framework follow a canonical layout that
keeps step models, workflow graphs, state factories, and runner factories
independent. See ``AGENTS.md`` (*Applications: canonical layout* section) and
the reference implementation at ``pyswark/apps/baseball/``:

.. code-block::

   pyswark/apps/<app_name>/
   ├── steps/        # Compute models, one per file
   ├── workflows/    # Workflow INSTANCES composing steps
   ├── states/       # State factories (create(**kw) -> State)
   └── runner/       # Runner factories wiring workflow + state by python:// refs
