# Architecture — pyswark

## Overview

pyswark is structured as a layered Python library. Dependencies flow strictly in one
direction: **foundation → framework → application**. This constraint is the single most
important architectural invariant in the codebase.

## Layer model

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (L2)                    │
│  gluedb · sekrets · workflow · tensor · ts · query          │
│  Domain-specific packages that users interact with most.    │
├─────────────────────────────────────────────────────────────┤
│                    Core Layer (L1)                           │
│  core.io · core.models · core.fsspec · core.extractor       │
│  I/O framework, URI routing, fsspec integration, models.    │
├─────────────────────────────────────────────────────────────┤
│                    Foundation Layer (L0)                     │
│  lib.pydantic · lib.aenum · lib.enum · lib.fsspec           │
│  Extensions to third-party libraries. Importable anywhere.  │
├─────────────────────────────────────────────────────────────┤
│                    Cross-cutting                             │
│  util (logging) · infra (version, packaging, test driver)   │
│  Side-effect-free; no upward dependencies.                  │
└─────────────────────────────────────────────────────────────┘
```

### Dependency rules

| From → To      | lib (L0) | core (L1) | app (L2) | util | infra |
|-----------------|----------|-----------|----------|------|-------|
| **lib (L0)**    | ✓ self   | ✗         | ✗        | ✓    | ✗     |
| **core (L1)**   | ✓        | ✓ self    | ✗        | ✓    | ✗     |
| **app (L2)**    | ✓        | ✓         | ✓ self*  | ✓    | ✗     |
| **util**        | ✗        | ✗         | ✗        | ✓    | ✗     |
| **infra**       | ✓        | ✓         | ✓        | ✓    | ✓     |

*Application packages may depend on each other where documented (e.g. `sekrets` uses
`gluedb` patterns), but circular dependencies are forbidden.

## Domain map

### lib — Foundation (L0)

| Module | Purpose |
|--------|---------|
| `lib.pydantic.base` | Shared Pydantic `BaseModel` with project defaults |
| `lib.pydantic.ser_des` | Type-preserving JSON: `toJson` / `fromJson` with embedded model paths |
| `lib.aenum` | `AliasEnum` and `Alias` for registry patterns |
| `lib.enum` | Standard enum extensions |
| `lib.fsspec` | Lower-level fsspec implementation registration |

### core — Framework (L1)

| Module | Purpose |
|--------|---------|
| `core.io.api` | Public API: `read()`, `write()`, `acquire()`, `isUri()`, `guess()` |
| `core.io.iohandler` | `IoHandler(Extractor)` — normalizes URI, selects `DataHandler` |
| `core.io.guess` | `Ext` / `Scheme` AliasEnums → handler class from extension or scheme |
| `core.io.datahandler` | `DataHandler` enum maps names → import paths via `pydoc.locate` |
| `core.io.base` | `AbstractDataHandler` — `UriModel`, fsspec `open`, logging, overwrite rules |
| `core.io.decorate` | `Log` / `Kwargs` decorators for I/O operations |
| `core.io.{df,json,yaml,python,url,text,string,...}` | Concrete format handlers |
| `core.models.uri` | Pluggable URI models (`UriModel.register`, LRU guess) |
| `core.models.db` | `MixinDb` / SQL-backed record DB, `connect()` context manager |
| `core.models.{record,body,info,collection,datetime,...}` | Domain value objects |
| `core.extractor` | `Extractor` base class (`extract()`) on Pydantic `BaseModel` |
| `core.fsspec` | Wraps fsspec; registers implementations; `fix.py` injects sekrets for `@username` URIs |

### Application packages (L2)

| Package | Purpose |
|---------|---------|
| `gluedb` | Data catalog — named records (often URIs) in a persistent `.gluedb` file. `Db`, `Hub`, SQLModel views. |
| `sekrets` | Credential hub — typed secrets resolved by protocol name. Built on GlueDb patterns. |
| `workflow` | Cached multi-step pipelines — `Workflow`, `Step`, `State` with input/output comparison. |
| `tensor` | Validated numpy types — `Tensor`, `TensorFrame`, `TensorDict`. |
| `ts` | Time series — `TsVector`, `DatetimeList`, timezone helpers. |
| `query` | Structured querying — `Interface`, `DataFrameQuery`, model-based and native backends. |

## I/O data flow

```
User calls api.read(uri)
  → IoHandler normalizes URI and DataHandler selection
    → guess.api(uri) builds UriModel, matches Ext or Scheme to handler class
      → DataHandler.get(name) resolves import path via pydoc.locate
        → AbstractDataHandler._read() with UriModel + fsspec open
          → (if @username in URI) fix.py resolves credentials via sekrets
            → Returns deserialized data
```

## Key patterns

1. **Registry via AliasEnum** — `DataHandler`, `Ext`, `Scheme` enums map string aliases
   to implementation paths, resolved lazily at runtime.
2. **Strategy handlers** — `AbstractDataHandler` defines the contract; concrete handlers
   per format (`df`, `json`, `yaml`, `python`, `url`, `text`, `string`, ...).
3. **URI polymorphism** — `UriModel` with pluggable scheme-specific models and guess fallback.
4. **Pydantic everywhere** — Models, extractors, I/O handlers, workflow state are all Pydantic.
5. **Decorator composition** — `Log.decorate` for tracing, `Kwargs` for injection, `fix.open`/`fix.filesystem` for fsspec wrapping.
6. **Context-managed persistence** — `Db.connect(uri, persist=True)` loads on enter, saves on successful exit.

## External dependencies

From `conda-recipe/meta.yaml` (authoritative source):

- **Runtime:** Python ≥3.9, PyYAML, numpy, pandas, pyarrow, sqlmodel, sqlalchemy,
  pydantic, fsspec, requests, aiohttp, aenum, holoviews, panel, bokeh, jupyter_bokeh
- **Optional:** pydrive2 (Google Drive via sekrets)
- **Build:** conda-build, setuptools
- **Test:** coverage, pytest (via ci/ requirements)

## Configuration

| What | Where |
|------|-------|
| Version, deps, entry points | `conda-recipe/meta.yaml` (single source of truth) |
| Setuptools wiring | `setup.py` (reads meta.yaml) |
| Package data manifest | `pyswark/package.data.yaml` |
| Sphinx docs config | `rtd/source/conf.py` (reads version from meta.yaml) |
| CI environments | `ci/test-env-requirements.yml`, `ci/rtd-env-requirements.yml` |
