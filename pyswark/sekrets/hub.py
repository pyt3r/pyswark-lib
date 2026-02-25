from functools import wraps

from pyswark.gluedb import hub
from pyswark.sekrets.settings import Settings


def _resolve_setting_name(name: str) -> str:
    """
    Normalize a protocol/db name through Settings.

    This allows callers to use any alias defined on Settings while the
    underlying hub always uses the canonical Settings member name.
    """
    return Settings.get(name).name


def _resolve_db_name(param: str, arg_index: int):
    """
    Decorator factory to rewrite the hub *db name* parameter using Settings.

    param      : the keyword parameter name to rewrite when passed by kw
    arg_index  : index in *args (after self) when passed positionally
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            # Prefer explicit keyword argument if present
            if param in kwargs:
                kwargs[param] = _resolve_setting_name(kwargs[param])
            else:
                # Fallback to positional argument at arg_index
                args = list(args)
                if len(args) > arg_index:
                    args[arg_index] = _resolve_setting_name(args[arg_index])
                args = tuple(args)
            return fn(self, *args, **kwargs)

        return wrapper

    return decorator


class Hub( hub.Hub ):
    """
    Secrets-aware Hub.

    This Hub behaves like the standard GlueDb Hub but automatically resolves
    database names through ``Settings.get(name)`` so callers can use protocol
    aliases (e.g. ``'sgdrive2'`` or ``'gdrive2'``) instead of the internal
    Settings enum member names.
    """

    @_resolve_db_name(param="name", arg_index=0)
    def extract(self, name):
        return super().extract(name)

    @_resolve_db_name(param="name", arg_index=1)
    def load(self, data, name):
        return super().load(data, name)

    @_resolve_db_name(param="dbName", arg_index=1)
    def postToDb(self, obj, dbName, name=None, overwrite=True):
        return super().postToDb(obj, dbName, name=name, overwrite=overwrite)

    @_resolve_db_name(param="dbName", arg_index=1)
    def putToDb(self, obj, dbName, name=None, overwrite=True):
        return super().putToDb(obj, dbName, name=name, overwrite=overwrite)

    @_resolve_db_name(param="dbName", arg_index=1)
    def mergeToDb(self, otherDb, dbName, overwrite=True):
        return super().mergeToDb(otherDb, dbName, overwrite=overwrite)

    @_resolve_db_name(param="dbName", arg_index=0)
    def deleteFromDb(self, dbName, name, overwrite=True):
        return super().deleteFromDb(dbName, name, overwrite=overwrite)

    @_resolve_db_name(param="dbName", arg_index=0)
    def getFromDb(self, dbName, name):
        return super().getFromDb(dbName, name)

    @_resolve_db_name(param="dbName", arg_index=0)
    def extractFromDb(self, dbName, name):
        return super().extractFromDb(dbName, name)

    @_resolve_db_name(param="dbName", arg_index=0)
    def acquireFromDb(self, dbName, name):
        return super().acquireFromDb(dbName, name)
