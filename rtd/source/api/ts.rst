ts - Time Series
================

The ``ts`` module provides time series primitives with datetime validation
and timezone support. This is Layer 2 of the architecture.

Key Features
------------

- **DatetimeList**: A validated list of datetime objects
- **TsVector**: A time series vector with datetime index and numeric values
- **Timezone support**: Convert between timezones
- **Efficient storage**: Store as base + deltas for compact serialization

Classes
-------

TsVector
^^^^^^^^

.. autoclass:: pyswark.ts.tsvector.TsVector
   :members:
   :undoc-members:
   :show-inheritance:

DatetimeList
^^^^^^^^^^^^

.. autoclass:: pyswark.core.models.datetime.DatetimeList
   :members:
   :undoc-members:
   :show-inheritance:

Datetime
^^^^^^^^

.. autoclass:: pyswark.core.models.datetime.Datetime
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Creating a TsVector
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.ts.tsvector import TsVector

   # Create from lists
   ts = TsVector(
       index=['2024-01-01', '2024-01-02', '2024-01-03'],
       values=[100.0, 101.5, 99.8]
   )

   print(len(ts))        # 3
   print(ts.dt)          # datetime64 array
   print(ts.values)      # Vector object

Working with DatetimeList
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.core.models.datetime import DatetimeList

   # Create from strings
   dates = DatetimeList(['2024-01-01', '2024-01-02', '2024-01-03'])
   print(len(dates))     # 3
   print(dates.dt)       # array of datetime64

   # Create from datetime objects
   import datetime
   dates2 = DatetimeList([
       datetime.datetime(2024, 1, 1),
       datetime.datetime(2024, 1, 2),
   ])

   # Resample to different resolution
   monthly = dates.resample('M')

Working with Datetime
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.core.models.datetime import Datetime

   # Create with timezone
   dt = Datetime('2024-01-15T10:30:00', dtype='s', tzname='UTC')

   # Convert to another timezone
   dt_eastern = dt.toTimezone('US/Eastern')

   # Get current time
   now = Datetime.now(tzname='UTC')

Serialization
^^^^^^^^^^^^^

Time series objects are fully serializable:

.. code-block:: python

   from pyswark.ts.tsvector import TsVector
   from pyswark.lib.pydantic import ser_des

   ts = TsVector(
       index=['2024-01-01', '2024-01-02'],
       values=[100.0, 101.5]
   )

   # Serialize
   json_str = ser_des.toJson(ts)

   # Deserialize
   restored = ser_des.fromJson(json_str)

