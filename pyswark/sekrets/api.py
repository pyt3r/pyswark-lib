"""
Secrets Management API
======================

This module provides a secure API for accessing credentials and secrets.
Secrets are stored in GlueDb databases organized by protocol and accessed
by username.

Security Note
-------------
This module connects to encrypted secret stores. Actual credentials
should never be committed to source control.

Example
-------
>>> from pyswark.sekrets import api
>>>
>>> # Get credentials for a specific service
>>> creds = api.get('myusername', 'sgdrive2')
"""

from pyswark.core.io import api


def get( protocol, name ):
    """
    Retrieve credentials for a name and protocol.

    Parameters
    ----------
    protocol : str
        The protocol/service name (e.g., 'gdrive2').
    name : str
        The username/identifier for the credential.

    Returns
    -------
    Any
        The credential object (structure depends on protocol).

    Example
    -------
    >>> creds = get('sgdrive2', 'myuser')
    """
    hub = getHub()
    return hub.extractFromDb( protocol, name )


def getHub():
    """
    Get the central secrets hub.

    Returns
    -------
    Hub
        The hub containing all protocol-specific secret databases.
    """
    from pyswark.sekrets import hubdata
    return api.read( f"python://{ hubdata.__name__}.HUB" )


def getDb( protocol ):
    """
    Get the secrets database for a protocol.

    Parameters
    ----------
    protocol : str
        The protocol name.

    Returns
    -------
    GlueDb
        The secrets database for this protocol.
    """
    hub = getHub()
    return hub.extract( protocol )


def Db():
    """ create a new database """
    from pyswark.sekrets import db
    return db.Db()

def sekret( name ):
    """ Get the model for a sekret """
    from pyswark.sekrets.models.enum import Models
    return Models.get( name ).klass
