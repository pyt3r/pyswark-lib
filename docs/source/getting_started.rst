Getting Started
===============

Installation
------------

Install pyswark using conda:

.. code-block:: bash

   conda install -c pyt3r pyswark



Example Capabilities
--------------------

1. Serialization with Type Preservation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A core tenet of pyswark is type-preserving serialization:

.. code-block:: python

   from pydantic import BaseModel
   from pyswark.lib.pydantic import ser_des

   class Character(BaseModel):
       name: str
       role: str

   mulder = Character(name='Fox Mulder', role='FBI Agent')

   # Serialize with embedded type information
   json_data = ser_des.toJson(mulder, indent=2)
   print(json_data)
   # {
   #   "model": "__main__.Character",
   #   "contents": {"name": "Fox Mulder", "role": "FBI Agent"}
   # }

   # Deserialize - no type hint needed!
   restored = ser_des.fromJson(json_data)
   assert type(restored) == Character


2. Unified I/O
^^^^^^^^^^^^^^

Read and write data from any URI:

.. code-block:: python

   from pyswark.core.io import api as io

   # Read from package data
   df = io.read('pyswark:/data/ohlc-jpm.csv.gz')

   # Write to file
   io.write(df, 'file:./output.csv')


3. Data Catalogs with GlueDb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create and use data catalogs:

.. code-block:: python

   from pyswark.gluedb import api
   from pyswark.core.models import collection

   # Connect to existing catalog
   db = api.connect('pyswark:/data/sma-example.gluedb')
   print(db.getNames())  # ['JPM', 'BAC', 'kwargs']

   # Extract data by name
   jpm_data = db.extract('JPM')
   kwargs   = db.extract('kwargs')


   # Create a new catalog
   from pyswark.gluedb import db
   new_db = db.Db()
   new_db.post("pyswark:/data/ohlc-jpm.csv.gz", name='JPM')
   new_db.post(collection.Dict({'window': 60}), name='kwargs')

   # Extract from a new catalog
   new_jpm_data = new_db.extract('JPM')
   new_kwargs   = new_db.extract('kwargs')

   # persist the new catalog
   from pyswark.core.io import api
   api.write( new_db, 'file:./new.gluedb' )


4. Time Series with DatetimeList and TsVector
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Work with validated time series data:

.. code-block:: python

   from pyswark.core.models.datetime import DatetimeList
   from pyswark.ts.tsvector import TsVector

   # Create a DatetimeList from strings
   dates = DatetimeList(['2024-01-01', '2024-01-02', '2024-01-03'])
   print(dates.dt)      # array of datetime64

   # Resample to different time resolution
   monthly = dates.resample('M')  # Convert to monthly resolution (lags to next month)
   print( monthly.dt ) # array(['2024-02', '2024-02', '2024-02'], dtype='datetime64[M]')

   # Create a time series vector
   ts = TsVector(
      index=['2024-01-01', '2024-01-02', '2024-01-03'],
      values=[100.0, 101.5, 99.8]
   )
   print(ts.dt)          # datetime64 array
   print(ts.values.vector)  # numpy array of values

   # DatetimeList efficiently stores as base + deltas
   dates = DatetimeList([2020, 2021, 2022, 2023])
   print(dates.basedt)   # 2020
   print(dates.deltas)   # [0, 1, 2, 3]

   # Fully serializable
   from pyswark.lib.pydantic import ser_des
   json_str = ser_des.toJson(ts)
   restored = ser_des.fromJson(json_str)


5. Workflow Orchestration
^^^^^^^^^^^^^^^^^^^^^^^^^

Orchestrate multi-step computations with automatic caching:

.. code-block:: python

   from from pyswark.workflow.workflow import Workflow
   from pyswark.workflow.step import Step
   from pyswark.workflow.state import State
   from pyswark.lib.pydantic import base

   # Define models with run() methods
   class AddModel(base.BaseModel):
      a: int
      b: int
      def run(self):
         return {'sum': self.a + self.b}

   class MultiplyModel(base.BaseModel):
      sum: int
      factor: int
      def run(self):
         return {'product': self.sum * self.factor}

   # Create workflow steps
   step0 = Step(
      model=AddModel,
      inputs={'x': 'a', 'y': 'b'},      # state → model inputs
      outputs={'sum': 'result'}          # model outputs → state
   )

   step1 = Step(
      model=MultiplyModel,
      inputs={'result': 'sum', 'z': 'factor'},
      outputs={'product': 'final'}
   )

   workflow = Workflow(steps=[step0, step1])

   # Initialize state with input data
   inputData = {'x': 2, 'y': 3, 'z': 4}
   state = State(backend=inputData)

   # Run workflow - steps execute in order
   result = workflow.run(state)
   print(result)  # {'final': 20}  # (2+3)*4

   # Workflows cache inputs/outputs - rerun skips unchanged steps
   print(workflow.stepsRan)      # [0, 1] - both ran
   print(workflow.stepsSkipped)  # []

   # Second run with same inputs - steps are skipped! 
   # - workflow cached its previous results and sees no need to recompute
   state2 = State(backend=inputData)
   workflow.run(state2)
   print(workflow.stepsSkipped)  # [0, 1] - both skipped!

