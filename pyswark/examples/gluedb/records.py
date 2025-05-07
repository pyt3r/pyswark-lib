from pyswark.examples.gluedb.settings import Settings
from pyswark.gluedb.db import Contents

RECORDS_1 = [
    { "info" : { "name" : "a" },
      "body" : {
          "model" : Contents.getUri(),
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.A", } }
    },
    { "info" : { "name" : "b" },
      "body" : {
          "model" : Contents.getUri(),
          "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.B", } }
    },
]

RECORDS_2 = [
    { "info" : { "name" : "c" },
      "body" : {
          "model" : Contents.getUri(),
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.C", } }
    },
    { "info" : { "name" : "d" },
      "body" : {
          "model" : Contents.getUri(),
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.D", } }
    },
]
