=============================================================
template-package : python + azure + conda + docs
=============================================================

This is a sample repo for demonstrating template CI pipelines.

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

.. |docs| image:: https://readthedocs.org/projects/template-package/badge/?version=latest
    :target: `Read the Docs`_
    :alt: Docs

.. |build| image:: https://img.shields.io/azure-devops/build/pyt3r/template/3
    :alt: Build
    :target: `Azure Pipeline`_

.. |coverage| image:: https://img.shields.io/azure-devops/coverage/pyt3r/template/3
    :alt: Coverage
    :target: `Azure Pipeline`_

.. |version| image:: https://img.shields.io/conda/v/pyt3r/template
    :alt: Version
    :target: `Anaconda Cloud`_

.. |platform| image:: https://img.shields.io/conda/pn/pyt3r/template
    :alt: Platform
    :target: `Anaconda Cloud`_

.. |downloads| image:: https://img.shields.io/conda/dn/pyt3r/template
    :alt: Platform
    :target: `Anaconda Cloud`_

.. end badges

.. links

.. _conda-build: https://docs.conda.io/projects/conda-build/en/latest/
.. _Azure Pipeline: https://dev.azure.com/pyt3r/template/_build
.. _Anaconda Cloud: https://anaconda.org/pyt3r/template
.. _Read the Docs: https://template-package.readthedocs.io

.. _(mini)conda: https://docs.conda.io/en/latest/miniconda.html
.. _conda-recipe/meta.yaml: conda-recipe/meta.yaml
.. _azure-pipelines.yml: azure-pipelines.yml
.. _https://dev.azure.com/pyt3r/template/_build: https://dev.azure.com/pyt3r/template/_build
.. _https://anaconda.org/pyt3r/template: https://anaconda.org/pyt3r/template
.. _.readthedocs.yml: .readthedocs.yml
.. _https://template-package.readthedocs.io: https://template-package.readthedocs.io
.. _MIT License: LICENSE

.. end links

.. contents:: :local:

Features
################

* triggers a template `Azure Pipeline`_ to build, test, and publish a conda package artifact
* triggers a template `Read the Docs`_ pipeline to build, publish, and deploy an html artifact

Prerequisites
################

* `(mini)conda`_
* python3.7
* Unix

Azure Builds
################

Each commit (and PR) to the master branch invokes the `azure-pipelines.yml`_ script, which automates Steps 1 through 3 below.

1. Create and activate a conda environment::

    $ make test-env
    $ conda activate test-env

2. Build and add the template package to the environment::

    (test-env) $ make conda-package

3. Run the tests against the template package and view the report::

    (test-env) $ make test-package


The Azure pipeline concludes by publishing the coverage report and conda package artifact to: `https://dev.azure.com/pyt3r/template/_build`_

.. image:: images/artifacts.png

Users may now access and upload the conda artifact to Anaconda Cloud.  The current build is published to: `https://anaconda.org/pyt3r/template`_

4. (Optional) Upload the artifact (requires an Anaconda account)::

    (test-env) $ anaconda upload ./template*.tar.bz2

   Once uploaded, the package may be installed as follows::

    $ conda install -c pyt3r template



Read The Docs
################

Each commit (and PR) to the master branch will also invoke the `.readthedocs.yml`_ script to build the documentation.

Upon a successful build, the resulting html artifact is deployed to: `https://template-package.readthedocs.io`_

Author
################

* ``pyt3r``

License
################

* `MIT License`_
