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

from functools import lru_cache
from pyswark.core.io import api
from pyswark.sekrets.settings import Settings


def get( username, protocol ):
    """
    Retrieve credentials for a username and protocol.

    Parameters
    ----------
    username : str
        The username/identifier for the credential.
    protocol : str
        The protocol/service name (e.g., 'sgdrive2').

    Returns
    -------
    Any
        The credential object (structure depends on protocol).

    Example
    -------
    >>> creds = get('myuser', 'sgdrive2')
    """
    db = getDb( _getProtocolName( protocol ))
    return db.extract( username )

@lru_cache()
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
    return hub.extract(_getProtocolName(protocol))

@lru_cache()
def getHub():
    """
    Get the central secrets hub.

    Returns
    -------
    Hub
        The hub containing all protocol-specific secret databases.
    """
    from pyswark.sekrets import hub

    return api.read( f"python://{ hub.__name__}.HUB" )

@lru_cache()
def _getProtocolName( protocol ):
    """Get the canonical protocol name from settings."""
    return Settings.get( protocol ).name

