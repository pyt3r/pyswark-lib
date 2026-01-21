import logging
from contextlib import contextmanager

logger = logging.getLogger('pyswark')
logger.setLevel(logging.DEBUG)


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)


fmt = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
ch.setFormatter(fmt)

logger.addHandler(ch)


def get_verbosity():
    """
    Get the current verbosity level.
    
    Returns
    -------
    int
        The current logging level (e.g., logging.INFO, logging.WARNING).
    
    Examples
    --------
    >>> from pyswark.util.log import get_verbosity
    >>> import logging
    >>> level = get_verbosity()
    >>> level == logging.INFO
    True
    """
    return logger.level


def set_verbosity(level):
    """
    Set the verbosity level for pyswark logging.
    
    This can be called multiple times at runtime to change the verbosity
    level. The change takes effect immediately and affects all subsequent
    logging operations.
    
    Parameters
    ----------
    level : str or int
        Logging level. Can be one of:
        - 'DEBUG' or logging.DEBUG (10) - Most verbose
        - 'INFO' or logging.INFO (20) - Default informational messages
        - 'WARNING' or logging.WARNING (30) - Only warnings and errors
        - 'ERROR' or logging.ERROR (40) - Only errors
        - 'CRITICAL' or logging.CRITICAL (50) - Only critical errors
        
        Can also be a string like 'debug', 'info', 'warning', 'error', 'critical'
        (case-insensitive).
    
    Examples
    --------
    >>> from pyswark.util.log import set_verbosity
    >>> set_verbosity('WARNING')  # Suppress INFO messages
    >>> set_verbosity(logging.ERROR)  # Only show errors
    >>> set_verbosity('debug')  # Show all messages
    >>> set_verbosity('INFO')  # Restore default
    """
    if isinstance(level, str):
        level = level.upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        if level not in level_map:
            raise ValueError(
                f"Invalid verbosity level '{level}'. "
                f"Must be one of: {list(level_map.keys())}"
            )
        level = level_map[level]
    
    logger.setLevel(level)
    ch.setLevel(level)


@contextmanager
def verbosity(level):
    """
    Context manager for temporarily setting verbosity level.
    
    The verbosity level is changed for the duration of the context
    and automatically restored when exiting.
    
    Parameters
    ----------
    level : str or int
        Logging level to use temporarily. See set_verbosity() for details.
    
    Examples
    --------
    >>> from pyswark.util.log import verbosity
    >>> from pyswark.core.io import api as io
    >>> 
    >>> # Most operations are quiet
    >>> with verbosity('WARNING'):
    ...     df1 = io.read('file:./data1.csv')  # No logging
    ...     df2 = io.read('file:./data2.csv')  # No logging
    ... 
    >>> # But this one we want to see
    >>> with verbosity('INFO'):
    ...     df3 = io.read('file:./important.csv')  # Shows logging
    ... 
    >>> # Verbosity automatically restored to previous level
    """
    old_level = get_verbosity()
    try:
        set_verbosity(level)
        yield
    finally:
        set_verbosity(old_level)
