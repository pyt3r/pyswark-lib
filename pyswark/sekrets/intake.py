from typing import Any, Optional

from pyswark.gluedb import db

from pyswark.lib.pydantic import base
from pyswark.core.io import contents, api
from pyswark.core.models import infer


# Default model URI for sekret records
DEFAULT_CONTENTS_MODEL = "python://pyswark.sekrets.models.generic.Contents"


class Intake(base.BaseModel):
    """
    Ingests unstructured data and converts to structured formats.
    
    Usage:
        # From raw data (dict, list, etc.)
        intake = Intake.ingest({"key1": "value1", "key2": "value2"})
        
        # From URI
        intake = Intake.ingest("file://config.json")
        
        # Convert to GlueDb sekret records
        records = intake.asSekretRecords()
        
        # Export
        intake.export("file://output.json")
    """
    
    raw: Any  # The ingested raw data (after inference/extraction)
    source: Optional[str] = None  # Original URI if applicable
    
    # ─────────────────────────────────────────────────────────────
    # Factory Methods
    # ─────────────────────────────────────────────────────────────
    
    @classmethod
    def ingest(cls, data: Any, datahandler: str = "", **kw) -> "Intake":
        """
        Ingest data from various sources.
        
        For URIs: reads and extracts the data
        For raw data: uses Infer().asCollection().asDict().extract()
        """
        if cls._isUri(data):
            raw = api.read( data, datahandler=datahandler, **kw )
            return cls( raw=raw, source=data )
        
        # Non-URI: use inference pipeline
        raw = cls._inferAsDict( data )
        return cls( raw=raw, source=None )
    
    @classmethod
    def _inferAsDict(cls, data: Any) -> dict:
        """
        Infer structure and convert to dict.
        Uses: Infer(data).asCollection().asDict().extract()
        """
        inferred = infer.Infer(data)
        collection = inferred.asCollection()
        dic = collection.asDict()
        return dic.extract()
    
    @staticmethod
    def _isUri(data) -> bool:
        """Detect if data looks like a URI."""
        if not isinstance(data, str):
            return False
        return ":/" in data or data.startswith(("/", "./", "~"))
    
    # ─────────────────────────────────────────────────────────────
    # Conversion to Sekret Records Format
    # ─────────────────────────────────────────────────────────────
    
    def asSekretRecords(
        self,
        model: str = DEFAULT_CONTENTS_MODEL,
        description: str = ""
    ) -> list:
        """
        Convert to list of records for a Sekret GlueDb model.
        
        Each key-value pair becomes:
        {
            "info": {"name": <key>},
            "body": {
                "model": <model>,
                "contents": <value>
            }
        }
        """
        data = self.raw

        Db = self._getDbModel(model)
        
        records = []
        for name, body in data.items():
            contents = self._fixContents( body, Db.Contents )
            record   = self._fixRecord( contents, name, Db.Record )
            records.append( record )
        return records

    @staticmethod
    def _getDbModel(model: str):
        """Get the Record model class for the given model URI."""
        Contents = api.read(model)
        return db.makeDb(Contents)
        
    @staticmethod
    def _fixContents(body: dict, Contents: db.Contents):

        if isinstance(body, Contents):
            return body
        
        if not isinstance(body, dict):
            """ default to generic sekret model """
            body = { "sekret": body }
        
        if isinstance(body, dict):
            return Contents(**body)
        
    @staticmethod
    def _fixRecord(contents: db.Contents, name: str, Record: db.Record):
        record = Record(contents, name=name)
        return { 
            'info' : { 'name': name }, 
            'body' : record.body,
        }
    
    # ─────────────────────────────────────────────────────────────
    # Conversion to GlueDb
    # ─────────────────────────────────────────────────────────────
    
    def asGlueDb(self, model: str = DEFAULT_CONTENTS_MODEL):
        """
        Convert to a GlueDb with sekret records.
        
        The model can be dynamically loaded via: api.read(model)
        """
        if isinstance(self.raw, db.GlueDb):
            return self.raw
        
        records = self.asSekretRecords( model=model )

        Db = self._getDbModel(model)
        return Db(records=records)
    
    def asSekretDb(self, model: str = DEFAULT_CONTENTS_MODEL):
        """
        Shorthand for asGlueDb with default sekret Contents model.
        """
        return self.asGlueDb( model=model )
    
    # ─────────────────────────────────────────────────────────────
    # Export Methods
    # ─────────────────────────────────────────────────────────────
    
    def export(self, uri: str, datahandler: str = "", as_records: bool = True, **kw):
        """
        Export to a target URI.
        
        Args:
            uri: Target URI
            datahandler: Optional handler (json, yaml, etc.)
            as_records: If True, exports as sekret records format
        """
        data = self.asSekretRecords() if as_records else self.raw
        c = contents.Contents(uri=uri, datahandler=datahandler, kw=kw)
        c.write(data)
        return uri
    
    def toJson(self, as_records: bool = True) -> str:
        """Serialize to JSON string."""
        import json
        data = self.asSekretRecords() if as_records else self.raw
        return json.dumps(data, indent=2, default=str)


# ─────────────────────────────────────────────────────────────
# Convenience API Functions
# ─────────────────────────────────────────────────────────────

def ingest(data: Any, **kw) -> Intake:
    """Ingest data into an Intake."""
    return Intake.ingest(data, **kw)


def toSekretRecords(data: Any, **kw) -> list:
    """Shorthand: ingest and convert to sekret records."""
    return Intake.ingest(data).asSekretRecords(**kw)

