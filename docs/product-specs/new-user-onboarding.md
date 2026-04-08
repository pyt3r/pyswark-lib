# New User Onboarding

**Status:** Active
**Date:** 2026-04

## Problem

New users encountering pyswark for the first time need a clear, progressive path
from installation to productive use. The library surface area is broad (I/O,
serialization, GlueDb, Sekrets, workflow, tensors, time series, queries) and
without guided onboarding, users either bounce off or only discover a fraction
of the capabilities.

## Users

- Python developers looking for a unified I/O and data management toolkit
- Data analysts who want lightweight catalog management without heavyweight infra
- Existing users exploring modules they haven't used yet

## Solution

### Installation path

1. **Conda install** (primary): `conda install -c pyt3r pyswark`
2. **Pip install** (secondary): from source via `setup.py`
3. **Verify**: `python -c "import pyswark; print(pyswark.__version__)"`

### Progressive learning journey

| Stage | What the user learns | Resource |
|-------|---------------------|----------|
| 1. Hello world | Install, import, read a local file | `rtd/source/getting_started.rst` §1 |
| 2. URI-based I/O | `api.read()` / `api.write()` with different schemes | `rtd/source/getting_started.rst` §2 |
| 3. Serialization | `ser_des.toJson()` / `fromJson()` round-trips | `rtd/source/getting_started.rst` §3 |
| 4. GlueDb | Create a catalog, add records, query | `rtd/source/getting_started.rst` §4 |
| 5. Time series | `DatetimeList`, `TsVector` | `rtd/source/getting_started.rst` §5 |
| 6. Workflow | Build a cached multi-step pipeline | `rtd/source/getting_started.rst` §6 |
| 7. Sekrets | Store and retrieve credentials | Blog: "Managing credentials with pyswark sekrets" |

### Entry point verification

The package provides a console entry point for quick verification:

```bash
pyswark-entry-point  # runs pyswark.scripts.hello:world
```

## Success criteria

- User can go from `conda install` to a working `api.read()` call in under 5 minutes
- Each stage builds on the previous one without requiring backtracking
- All examples in `getting_started.rst` run without modification on a fresh install

## Non-goals

- This spec does not cover API reference completeness (see `QUALITY_SCORE.md`)
- This spec does not cover contributor onboarding (see `AGENTS.md` for agent workflow)

## Dependencies

- `conda-recipe/meta.yaml` must be up to date with all runtime dependencies
- `rtd/source/getting_started.rst` must match current API surface
- Example scripts in `examples/` must be runnable and sphinx-gallery compatible
