from pyswark.tests.unittests.data.gluedb.settings import Settings
from pyswark.gluedb.models import IoModel

RECORDS_1 = [
    { "info" : {
        "name"          : "a",
        #"date_created"  : "2025-01-01T01:01:01", # optional
        #"date_modified" : "2025-01-01T02:02:02", # optional
    },
      "body" : {
          "model" : IoModel.getUri(),
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.A", } }
    },
    { "info" : {
        "name"          : "b",
        ##"date_created"  : "2025-01-01T01:01:01",
        #"date_modified" : "2025-01-01T02:02:02",
    },
      "body" : {
          "model" : IoModel.getUri(),
          "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.B", } }
    },
]

RECORDS_2 = [
    { "info" : {
        "name"          : "c",
        #"date_created"  : "2025-01-01T01:01:01",
        ##"date_modified" : "2025-01-01T02:02:02",
    },
      "body" : {
          "model" : IoModel.getUri(),
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.C", } }
    },
    { "info" : {
        "name"          : "d",
        ##"date_created"  : "2025-01-01T01:01:01",
        ##"date_modified" : "2025-01-01T02:02:02",
    },
      "body" : {
          "model" : IoModel.getUri(),
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.D", } }
    },
]
