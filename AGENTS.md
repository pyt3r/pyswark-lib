# AGENTS.md — pyswark

> This file is the entry point for agents working in this repository.
> It is intentionally short. Treat it as a table of contents, not an encyclopedia.
> Deeper context lives in the files linked below—read them as needed.

## What is pyswark?

A Python "swiss army knife" library providing unified URI-based I/O, type-preserving
serialization, data catalog management (GlueDb), credential handling (Sekrets),
workflow orchestration, and structured query interfaces. Distributed via conda
(channel: `pyt3r`), packaged with setuptools, config sourced from `conda-recipe/meta.yaml`.

## Repository layout

```
pyswark-lib/
├── pyswark/             # Main package
│   ├── lib/             # Layer 0 — Pydantic base, enums, aenum, fsspec wrappers
│   ├── core/            # Layer 1 — I/O framework, URI models, fsspec integration, extractors
│   ├── gluedb/          # Layer 2 — Data catalog (Db, Hub, models)
│   ├── sekrets/         # Layer 2 — Credential hub and protocol models
│   ├── workflow/        # Layer 2 — Workflow, Step, State orchestration
│   ├── tensor/          # Layer 2 — Validated numpy-oriented types
│   ├── ts/              # Layer 2 — Time series and datetime helpers
│   ├── query/           # Layer 2 — Structured querying interfaces
│   ├── util/            # Shared helpers (logging)
│   ├── infra/           # Version, package data, test driver
│   ├── scripts/         # Console entry points
│   ├── tests/           # Unit and integration tests
│   └── data/            # Packaged data assets
├── rtd/                 # Sphinx / Read the Docs source (source/, Makefile)
├── docs/                # Agent knowledge base (design docs, plans, specs, references)
├── examples/            # Runnable examples (sphinx-gallery source)
├── conda-recipe/        # meta.yaml — single source for version, deps, entry points
├── ci/                  # CI environment requirements
├── setup.py             # setuptools (reads meta.yaml)
├── Makefile             # test, docs, conda, lint targets
├── AGENTS.md            # Agent entry point (this file)
└── ARCHITECTURE.md      # Full architecture map
```

## Architecture (quick reference)

See `ARCHITECTURE.md` for the full map. The critical rule:

**lib → core → application packages.** Never import backwards.

- `lib/` may be imported anywhere (foundational extensions)
- `core/` depends on `lib/`, never on application packages
- Application packages (`gluedb`, `sekrets`, `workflow`, etc.) depend on `core/` and `lib/`
- `util/` is side-effect-free and importable from anywhere

## Knowledge base

All deep documentation lives in `docs/`. Navigate by topic:

| Need | File |
|------|------|
| Architecture & layering | `ARCHITECTURE.md` |
| Design principles | `docs/DESIGN.md` |
| Design documents catalog | `docs/design-docs/index.md` |
| Core beliefs & operating principles | `docs/design-docs/core-beliefs.md` |
| Current plans & roadmap | `docs/PLANS.md` |
| Active execution plans | `docs/exec-plans/active/` |
| Completed execution plans | `docs/exec-plans/completed/` |
| Technical debt tracking | `docs/exec-plans/tech-debt-tracker.md` |
| Product specs | `docs/product-specs/index.md` |
| New user onboarding | `docs/product-specs/new-user-onboarding.md` |
| Quality grades by module | `docs/QUALITY_SCORE.md` |
| Reliability practices | `docs/RELIABILITY.md` |
| Security & credentials | `docs/SECURITY.md` |
| Visualization / UI layer | `docs/FRONTEND.md` |
| Product sense & positioning | `docs/PRODUCT_SENSE.md` |
| Generated schemas | `docs/generated/db-schema.md` |
| External tool references | `docs/references/` |
| Blog posts (module context) | `docs/BLOG_POSTS.md` |

## Environment setup

Before running any Python code or tests, activate the conda environment and
ensure pyswark is importable:

```bash
conda activate test-env
cd pyswark-lib          # or: export PYTHONPATH="$PWD/pyswark-lib:$PYTHONPATH"
```

> Cursor agents: this is also configured in `.cursor/rules/pyswark-env.mdc`
> and will be injected automatically when working on `pyswark-lib/**` files.

## Development workflow

1. **Read before writing.** Always read the relevant module and its tests before modifying.
2. **Run tests.** `make test` from `pyswark-lib/`. Integration tests are in `pyswark/tests/integration/`.
3. **Respect layers.** Do not introduce backward imports. Check `docs/design-docs/core-beliefs.md` and `docs/DESIGN.md`.
4. **Update docs.** If you change public API or behavior, update Sphinx docs under `rtd/source/`.
5. **Version.** The single source of truth for version is `conda-recipe/meta.yaml`.
6. **Packaging.** `setup.py` reads from `meta.yaml`. Do not duplicate version or deps elsewhere.

## Key commands

```bash
make test           # Run unit tests with coverage
make docs-html      # Build Sphinx HTML docs (open in browser)
make conda-package  # Build conda package
make lint           # Run linters
make clean          # Remove build artifacts
```

## Conventions

- **Pydantic models** are the universal configuration/DTO layer.
- **AliasEnum** registries map string aliases to implementation paths (resolved via `pydoc.locate`).
- **URI polymorphism** — all I/O is addressed by URI; schemes route to handlers.
- **Decorators** for I/O tracing (`Log.decorate`) and kwargs injection.
- **Context managers** for DB persistence (`Db.connect(..., persist=True)`).
