API Reference
=============

This section provides detailed API documentation for all pyswark modules.
The package is organized into layers, with each layer building on the ones below it.

.. toctree::
   :maxdepth: 2
   :caption: Foundation Layer (Layer 0)

   lib

.. toctree::
   :maxdepth: 2
   :caption: Core Layer (Layer 1)

   core

.. toctree::
   :maxdepth: 2
   :caption: Application Layer (Layer 2)

   gluedb
   workflow
   tensor
   ts
   sekrets
   query


**Key principle**: Layers only import from lower layers, never from higher layers.


Quick Import Guide
------------------

.. code-block:: python

   # Serialization (lib layer)
   from pyswark.lib.pydantic import base, ser_des

   # I/O operations (core layer)
   from pyswark.core.io import api as io

   # Data catalogs (application layer)
   from pyswark.gluedb import api

   # Workflows
   from pyswark.workflow.workflow import Workflow
   from pyswark.workflow.step import Step

   # Tensors and time series
   from pyswark.tensor.tensor import Vector, Matrix
   from pyswark.ts.tsvector import TsVector

