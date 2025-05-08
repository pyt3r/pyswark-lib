from dateutil import tz
import numpy as np
from pyswark.lib.aenum import AliasEnum, Alias


class TzInfos( AliasEnum ):
    UTC = tz.gettz('UTC'), Alias("utc")
    EST = tz.gettz('America/New_York'), Alias("est")
    EDT = tz.gettz('America/New_York'), Alias("edt")
    CST = tz.gettz('America/Chicago'), Alias("cst")
    CDT = tz.gettz('America/Chicago'), Alias("cdt")
    MST = tz.gettz('America/Denver'), Alias("mst")
    MDT = tz.gettz('America/Denver'), Alias("mdt")
    PST = tz.gettz('America/Los_Angeles'), Alias("pst")
    PDT = tz.gettz('America/Los_Angeles'), Alias("pdt")

    # International examples
    GMT  = tz.gettz('Etc/GMT'), Alias("gmt") # Greenwich Mean Time
    CET  = tz.gettz('Europe/Paris'), Alias("cet")
    CEST = tz.gettz('Europe/Paris'), Alias("cest")
    IST  = tz.gettz('Asia/Kolkata'), Alias("ist")
    JST  = tz.gettz('Asia/Tokyo'), Alias("jst")
    AEST = tz.gettz('Australia/Sydney'), Alias("aest")
    AEDT = tz.gettz('Australia/Sydney'), Alias("aedt")
    NZST = tz.gettz('Pacific/Auckland'), Alias("nzst")
    NZDT = tz.gettz('Pacific/Auckland'), Alias("nzdt")


class OffsetUTC( AliasEnum ):
    UTC = np.timedelta64(  0 ), Alias("utc")
    EST = np.timedelta64( -4, 'h' ), Alias("est")
    EDT = np.timedelta64( -4, 'h' ), Alias("edt")
    CST = np.timedelta64( -6, 'h' ), Alias("cst")
    CDT = np.timedelta64( -5, 'h' ), Alias("cdt")
    MST = np.timedelta64( -7, 'h' ), Alias("mst")
    MDT = np.timedelta64( -6, 'h' ), Alias("mdt")
    PST = np.timedelta64( -8, 'h' ), Alias("pst")
    PDT = np.timedelta64( -7, 'h' ), Alias("pdt")