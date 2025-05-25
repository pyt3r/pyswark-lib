=============================================================
PySwark: my swiss army knife for everyday python
=============================================================

PySwark is a collection of Python tools I’ve built and found to be useful for a wide range of software tasks.


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

.. |docs| image:: https://readthedocs.org/projects/pyswark-lib/badge/?version=latest
    :target: `Read the Docs`_
    :alt: Docs

.. |build| image:: https://img.shields.io/azure-devops/build/pyt3r/pyswark/6
    :alt: Build
    :target: `Azure Pipeline`_

.. |coverage| image:: https://img.shields.io/azure-devops/coverage/pyt3r/pyswark/6
    :alt: Coverage
    :target: `Azure Coverage`_

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
.. _Azure Coverage: https://dev.azure.com/pyt3r/pyswark/_build/results?view=codecoverage-tab&buildId=329.. _Anaconda Cloud: https://anaconda.org/pyt3r/pyswark
.. _Read the Docs: https://pyswark-lib.readthedocs.io/en/latest/

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


Examples include..

* Simplified I/O APIs

  .. code-block:: python

    from pyswark.core.io import api

    df = api.read( 'pyswark://data/df.csv' )
    api.write( df, './df-copy.parquet' )

    dump = df.to_json()
    api.write( dump, './df-copy.json' )

    fn = api.read( 'python://pyswark.core.io.api.read' )
    assert fn == api.read

* (De)serialization support

  .. code-block:: python

    from pydantic import BaseModel
    from pyswark.lib.pydantic import ser_des

    class ModelXY( BaseModel ):
        x: int
        y: float

    model = ModelXY( x=1.0, y='2.2' )

    ser = ser_des.toJson( model )
    des = ser_des.fromJson( ser )

    assert isinstance( des, ModelXY )


* DataFrame-like structures for tensors, matrices, and vectors

  .. code-block:: python

    from pyswark.tensor.tensorframe import MatrixFrame

    mf = MatrixFrame({
        'x': [[ 1, 2, 3 ],
              [ 4, 5, 6] ],
        'y': [[ 1, -1, 1 ],
              [ -1, 1, -1] ],
    })
    print( mf['x'] * mf['y'] )
    """
    [[ 1 -2  3]
    [ -4  5 -6]]
    """


* A database for managing disorganized data


* And many others to explore on the `Read the Docs`_ page..
