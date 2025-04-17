=============================================================
PySwark: A Swiss Army Knife for everyday Python
=============================================================

PySwark houses the collection of Python tools that I’ve built and found to be useful for general software purposes.


.. badges

.. list-table::
    :stub-columns: 1
    :widths: 10 90

    * - docs
      - |docs|
    * - tests
      - |build| |coverage|
    * - package
      - |version| |platform| |downloads|

.. |docs| image:: https://readthedocs.org/projects/pyswark-package/badge/?version=latest
    :target: `Read the Docs`_
    :alt: Docs

.. |build| image:: https://img.shields.io/azure-devops/build/pyt3r/pyswark/5
    :alt: Build
    :target: `Azure Pipeline`_

.. |coverage| image:: https://img.shields.io/azure-devops/coverage/pyt3r/pyswark/5
    :alt: Coverage
    :target: `Azure Pipeline`_

.. |version| image:: https://img.shields.io/conda/v/pyt3r/pyswark
    :alt: Version
    :target: `Anaconda Cloud`_

.. |platform| image:: https://img.shields.io/conda/pn/pyt3r/pyswark
    :alt: Platform
    :target: `Anaconda Cloud`_

.. |downloads| image:: https://img.shields.io/conda/dn/pyt3r/pyswark
    :alt: Platform
    :target: `Anaconda Cloud`_

.. end badges

.. links

.. _conda-build: https://docs.conda.io/projects/conda-build/en/latest/
.. _Azure Pipeline: https://dev.azure.com/pyt3r/pyswark/_build
.. _Anaconda Cloud: https://anaconda.org/pyt3r/pyswark
.. _Read the Docs: https://pyswark-package.readthedocs.io

.. _(mini)conda: https://docs.conda.io/en/latest/miniconda.html
.. _conda-recipe/meta.yaml: conda-recipe/meta.yaml
.. _azure-pipelines.yml: azure-pipelines.yml
.. _https://dev.azure.com/pyt3r/pyswark/_build: https://dev.azure.com/pyt3r/pyswark/_build
.. _https://anaconda.org/pyt3r/pyswark: https://anaconda.org/pyt3r/pyswark
.. _.readthedocs.yml: .readthedocs.yml
.. _https://pyswark-package.readthedocs.io: https://pyswark-package.readthedocs.io
.. _MIT License: LICENSE

.. end links


Give it a try:

.. code-block:: bash

    $ conda install pyswark -c pyt3r


Examples include:

* Simplified I/O signatures

.. code-block:: python

    from pyswark.core.datahandler import api

    data = api.read( '/path/to/df.csv.gz' )
    api.write( data, '/path/to/df-copy.csv.gz' )

    data = api.read( 'file://path/to/data.json' )
    api.write( data, 'file://path/to/data-copy.json' )

    # import by uri
    read = api.read( 'python://pyswark.core.datahandler.api.read' )
    assert read == api.read

* (De)serialization methods

.. code-block:: python

    from pyswark.lib.pydantic import base, ser_des

    class ModelXY( base.BaseModel ):
        x: int
        y: float

    model = ModelXY( x=1.0, y='2.2' )

    ser = ser_des.toJson( model )
    des = ser_des.fromJson( ser )

    assert isinstance( des, ModelXY )


* A database for managing disorganized data


* And many more...
