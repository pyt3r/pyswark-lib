sekrets - Credential Management
===============================

The ``sekrets`` module provides secure credential management, connecting
to encrypted stores. This is Layer 2 of the architecture.

.. warning::

   Never commit actual credentials to source control. This module
   connects to external encrypted stores for credential retrieval.

Key Concepts
------------

- Credentials are organized by **protocol** (service type)
- Each protocol has its own GlueDb of credentials
- Credentials are accessed by **username**

API Functions
-------------

.. automodule:: pyswark.sekrets.api
   :members: get, getDb, getHub
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Getting Credentials
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.sekrets import api

   # Get credentials for a specific service
   creds = api.get('myusername', 'sgdrive2')

   # Use the credentials
   # (structure depends on the protocol)

Accessing the Secrets Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyswark.sekrets import api

   # Get the database for a protocol
   db = api.getDb('sgdrive2')

   # List available usernames
   print(db.getNames())

Configuration
-------------

Secrets configuration is managed through the ``Settings`` class and
external hub definitions. See the ``sekrets.settings`` and ``sekrets.hubdata``
modules for configuration details.

Security Best Practices
-----------------------

1. **Never hardcode credentials** - Always use this API
2. **Use environment variables** - For sensitive paths
3. **Encrypt at rest** - Use encrypted secret stores
4. **Limit access** - Apply principle of least privilege

