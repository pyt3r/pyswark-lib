workflow - Orchestration
========================

The ``workflow`` module provides orchestration of multi-step computations
with caching and reproducibility. This is Layer 2 of the architecture.

Key Concepts
------------

- **Workflow**: A sequence of Steps with input/output caching
- **Step**: A single unit of work with defined inputs and outputs
- **State**: Shared data store that persists between steps

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

Usage Examples
--------------

Basic Workflow
^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.workflow.workflow import Workflow
   from pyswark.workflow.step import Step
   from pyswark.workflow.state import State

   # Define steps
   workflow = Workflow(steps=[
       Step(
           model='mymodule.PreprocessModel',
           inputs={'raw_data': 'data'},      # state 'raw_data' → model input 'data'
           outputs={'processed': 'clean'}    # model output 'processed' → state 'clean'
       ),
       Step(
           model='mymodule.AnalysisModel',
           inputs={'clean': 'data'},
           outputs={'result': 'analysis'}
       ),
   ])

   # Initialize state with input data
   state = State()
   state.post('raw_data', my_dataframe)

   # Run the workflow
   result = workflow.run(state)

Workflow with Caching
^^^^^^^^^^^^^^^^^^^^^

Workflows automatically cache inputs and outputs. If you run the same
workflow with the same inputs, steps will be skipped:

.. code-block:: python

   # First run - all steps execute
   result1 = workflow.run(state)
   print(workflow.stepsRan)      # [0, 1]
   print(workflow.stepsSkipped)  # []

   # Second run - steps are skipped if inputs unchanged
   result2 = workflow.run(state)
   print(workflow.stepsRan)      # []
   print(workflow.stepsSkipped)  # [0, 1]

Creating a Model for Workflow Steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Models used in workflows should have a ``run()`` method that returns a dict:

.. code-block:: python

   from pyswark.lib.pydantic import base
   from pyswark.core.models import xputs

   class PreprocessModel(base.BaseModel):
       inputs: PreprocessInputs

       def run(self):
           # Computation here
           processed = self.inputs.data.dropna()
           return {'processed': processed}

   class PreprocessInputs(xputs.BaseInputs):
       data: Any

Inspecting Workflow State
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get cached inputs/outputs for a step
   model_input = workflow.getModelInput(0)
   model_output = workflow.getModelOutput(0)

   # Get the instantiated model
   model = workflow.getModel(0)

