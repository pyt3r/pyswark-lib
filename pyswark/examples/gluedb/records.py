from pyswark.examples.gluedb.settings import Settings

RECORDS_1 = [
    { "name" : "a",
      "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.A", }
    },
    { "name" : "b",
      "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.B", }
    },
]

RECORDS_2 = [
    { "name" : "c",
      "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.C", }
    },
    { "name" : "d",
      "contents": { "uri"  : f"{ Settings.OBJECTS.uri }.D", }
    },
]
