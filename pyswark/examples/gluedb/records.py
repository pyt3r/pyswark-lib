from pyswark.examples.gluedb.settings import Settings

RECORDS_1 = [
    { "info" : { "name" : "a" },
      "body" : {
          "model" : "pyswark.core.gluedb.db.Contents",
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.A", } }
    },
    { "info" : { "name" : "b" },
      "body" : {
          "model" : "pyswark.core.gluedb.db.Contents",
          "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.B", } }
    },
]

RECORDS_2 = [
    { "info" : { "name" : "c" },
      "body" : {
          "model" : "pyswark.core.gluedb.db.Contents",
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.C", } }
    },
    { "info" : { "name" : "d" },
      "body" : {
          "model" : "pyswark.core.gluedb.db.Contents",
          "contents" : { "uri"  : f"{ Settings.OBJECTS.uri }.D", } }
    },
]
