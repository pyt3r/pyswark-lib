# Generated: Database Schema Reference

> **Auto-generated reference.** This document describes the data models and schemas
> used by pyswark's persistence layers. Update this when models change.

## GlueDb schema

GlueDb stores heterogeneous data artifacts as named records in a flat-file
catalog (`.gluedb` extension). Each database is a collection of records
addressable by unique name.

### Record structure

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique identifier within the database |
| `body` | `Body` | Payload — typically a URI, dict, or serialized model |
| `info` | `Info` | Optional metadata (tags, timestamps, annotations) |

### Body types

The `Body` model is polymorphic. Common shapes:

- **URI body** — `body.uri: str` pointing to an external resource
- **Dict body** — `body.data: dict` with inline key-value data
- **Model body** — Serialized Pydantic model (via `ser_des.toJson`)

### Database file format

`.gluedb` files are JSON. Structure:

```json
{
  "name": "my-catalog",
  "records": {
    "record-name": {
      "name": "record-name",
      "body": { ... },
      "info": { ... }
    }
  }
}
```

### SQL views (SQLModel)

When accessed via `Db.connect()` with SQLModel, records are projected into
SQLAlchemy-compatible tables for querying:

| Table | Columns | Source |
|-------|---------|--------|
| `records` | `name`, `body_json`, `info_json` | GlueDb records |

Query example:

```python
from pyswark.gluedb.db import Db

with Db.connect("path/to/catalog.gluedb", persist=True) as db:
    results = db.query(name="my-record")
```

## Sekrets schema

The Sekrets hub stores credentials as GlueDb records with protocol-specific models.

### Protocol models

| Protocol | Module | Key fields |
|----------|--------|------------|
| GDrive service account | `sekrets.models.gdrive` | `service_account_file`, `scopes` |
| Generic key-value | `sekrets.models.*` | Protocol-dependent |

### Hub resolution

```
sekrets.api.get(protocol_name)
  → Hub.resolve(protocol_name)
    → Loads GlueDb record
      → Deserializes to protocol-specific Pydantic model
```

## URI models

URI models are registered in `core.models.uri` and selected via LRU-cached guessing.

| Scheme | Model | Handler |
|--------|-------|---------|
| `file://` | `FileUriModel` | Local filesystem |
| `http://`, `https://` | `HttpUriModel` | HTTP requests |
| `python://` | `PythonUriModel` | Python object import |
| `pyswark://` | `PyswarkUriModel` | Packaged data assets |
| `@username/...` | (fsspec + sekrets) | Credential-injected remote FS |

## DataHandler registry

| Handler name | Extension(s) | Format |
|-------------|-------------|--------|
| `df` | `.csv`, `.parquet` | DataFrame (pandas) |
| `json` | `.json` | JSON dict/list |
| `yaml` | `.yaml`, `.yml` | YAML dict |
| `text` | `.txt` | Plain text string |
| `python` | `python://` scheme | Python object import |
| `url` | `http://`, `https://` | URL fetch |
| `string` | — | Raw string passthrough |
| `gluedb` | `.gluedb` | GlueDb catalog |
| `pjson` | `.pjson` | Type-preserving JSON (ser_des) |
