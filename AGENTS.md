# AGENTS.md — pyswark

> This file is the entry point for agents working in this repository.
> It is a mix of table-of-contents pointers (for cross-cutting topics) and
> in-depth operational guides for areas used frequently enough to belong here
> directly — most notably the **Workflow framework** section near the bottom,
> which is the primary scaffold for every application under `pyswark/apps/`.
> For anything not covered here, follow the knowledge-base links below.

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
│   ├── workflow/        # Layer 2 — Workflow, Step, State, Runner orchestration
│   ├── tensor/          # Layer 2 — Validated numpy-oriented types
│   ├── ts/              # Layer 2 — Time series and datetime helpers
│   ├── query/           # Layer 2 — Structured querying interfaces
│   ├── apps/            # Layer 3 — User-facing applications built on the workflow framework
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
- `apps/` sit on top and may import any lower layer. `apps/` must NOT import each other.
- `util/` is side-effect-free and importable from anywhere

## Knowledge base

All deep documentation lives in `docs/`. Navigate by topic:

| Need | File |
|------|------|
| Architecture & layering | `ARCHITECTURE.md` |
| Workflow framework & app layout | *Workflow framework* / *Applications: canonical layout* sections below |
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

> Cursor agents: the rule is versioned at `pyswark-lib/.cursor/rules/pyswark-env.mdc`
> and injected automatically when working on `pyswark-lib/**` files.
> To install it as a symlink in the workspace run `make cursor-rules` from `pyswark-lib/`.

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

---

## Workflow framework

The `pyswark.workflow` package is the primary engine for building data
pipelines and analytics applications. It is the scaffold used by everything
under `pyswark/apps/`. Read this section before writing a new app.

### The four building blocks

| Concept  | Class(es)                                  | Module                        | Responsibility |
|----------|--------------------------------------------|-------------------------------|----------------|
| Step     | `Step`                                     | `pyswark.workflow.step`       | Wires a pydantic **model** (the compute) into state via name mappings |
| Workflow | `Workflow`, `Extracts`                     | `pyswark.workflow.workflow`   | Ordered list of `Step`s, with input/output caching ("extracts") for skip logic |
| State    | `Interface`, `State`, `StateWithGlueDb`    | `pyswark.workflow.state`      | Named key-value store shared across steps |
| Runner   | `Runner`                                   | `pyswark.workflow.runner`     | Assembles a `Workflow` + `State` (as instances or `python://` refs) and runs them |

### Step

A `Step` references a pydantic `BaseModel` class that implements `run() -> dict`.
The step declares two name mappings:

- `inputs`: `{state_name: model_field_name}` — pulled from state into the model's constructor.
- `outputs`: `{model_output_key: state_name}` — pushed from the model's `run()` result back into state.

```python
from pyswark.lib.pydantic import base
from pyswark.core.io import api as io

class ExtractModel(base.BaseModel):
    uri: str
    def run(self):
        return {'data': io.read(self.uri)}
```

```python
from pyswark.workflow.step import Step

step = Step(
    model   = 'mypkg.steps.extract.ExtractModel',
    inputs  = {'uri': 'uri'},           # state 'uri'  -> model field 'uri'
    outputs = {'data': 'raw_data'},     # model output 'data' -> state 'raw_data'
)
```

`model` may be a fully-qualified dotted path (string) or a class — it is
normalized to its URI string via the class's `getUri()` method. Models are
instantiated fresh each step run from the current state's values.

### State

A `State` holds named values shared across steps. Three classes:

- **`Interface`** — abstract base defining `extract(name)`, `post(data, name)`, `delete(name)`, `__contains__`, plus the `mutable: bool` flag.
- **`State`** — plain `dict` backend. Fastest, in-memory only.
- **`StateWithGlueDb`** — backend is a `gluedb.Db`, which means values are stored as typed pyswark records (auto-inferred via `Infer` if not already a `BaseModel`) with SQLite metadata. Enables persistence and richer introspection.

**Immutability matters.** By default `mutable=False`. Re-posting an existing
name raises (`ValueError` for `State`, `IntegrityError` for `StateWithGlueDb`).
This is what makes reruns safe — see "Skip semantics" below.

```python
from pyswark.workflow.state import State, StateWithGlueDb

state = State(backend={'uri': 'file:./input.csv'})
state = StateWithGlueDb(backend={'uri': 'file:./input.csv'})  # SQLite-backed
```

### Workflow

A `Workflow` is an ordered list of `Step`s plus two cache tables,
`modelInputs` and `modelOutputs` (both `Extracts`). Calling `workflow.run(state)`
iterates steps; each step's output is posted to state so downstream steps can
read it.

```python
from pyswark.workflow.workflow import Workflow
from pyswark.workflow.step import Step

WORKFLOW = Workflow(steps=[
    Step(model='mypkg.steps.extract.ExtractModel',
         inputs={'uri': 'uri'}, outputs={'data': 'raw_data'}),
    Step(model='mypkg.steps.transform.TransformModel',
         inputs={'raw_data': 'df'}, outputs={'out': 'clean_data'}),
])
```

Flags:

- `useExtracts` (default `True`) — consult the cache to skip steps whose current input matches the cached input.
- `populateExtracts` (default `True`) — write the current input/output back into the cache after each step.

Introspection after `run()`:

- `workflow.stepsRan` / `workflow.stepsSkipped` — lists of indices.
- `workflow.getModelInput(i)` / `getModelOutput(i)` — cached values.
- `workflow.getModel(i)` — reconstruct the model instance used at step i.

### Skip semantics (the "rerun is cheap" invariant)

Before running step `i`, the workflow:

1. Extracts current `modelInput` from state.
2. Checks if `useExtracts` and both `modelInputs[i]` and `modelOutputs[i]` are cached.
3. If cached **and** `modelInputs[i] == currentInput`, mark the step as skipped and use the cached `modelOutputs[i]`.
4. Otherwise, run the model fresh.

After the step (skip or run), the workflow posts outputs to state with the
**idempotent post** rule: if `skip=True`, only post output names not already
in state; if `skip=False`, post all outputs unconditionally. This makes
`workflow.run(state)` safely callable multiple times against an **immutable**
`StateWithGlueDb` — the second call is a no-op at the write layer. If you
need to force a clean re-run, pass `workflow.useExtracts = False` AND provide
a mutable or freshly-created state.

### Runner

A `Runner` assembles a workflow and state and runs them. Both may be provided
as instances OR as `python://module.path` reference strings, which are
resolved lazily by `pyswark.core.io.api.read` at run time. String refs are
preferred for the top-level app entry point because:

- They serialize cleanly (the reference round-trips; instances lose subclass type on `Union[str, Interface]` fields).
- `io.read` on `python://` defaults to `reloadmodule=True`, so every call re-imports the referenced module and produces **fresh** state/workflow instances — each `runner.run()` starts clean regardless of how the module-level object was mutated before.

```python
from pyswark.workflow.runner import Runner

runner  = Runner(workflow='python://mypkg.workflows.etl.WORKFLOW',
                 state   ='python://mypkg.states.season.SEASON_2023')
result  = runner.run()
# runner.rerunWorkflow and runner.rerunState hold the post-run instances
result2 = runner.rerun()  # idempotent: skips all steps (same inputs cached)
result3 = runner.rerun(useExtracts=False, populateExtracts=False)  # force re-execute
```

### Serialization

All workflow objects inherit `pyswark.lib.pydantic.base.BaseModel` and support
`toJson()` / `fromJson()` with type-preserving envelopes
(`{model: "module.Class", contents: {...}}`). Round-trip caveats:

- `Workflow`, `Step`, `Runner` round-trip cleanly when fields have concrete types.
- Fields typed `Union[str, SomeBaseClass]` (e.g., `Runner.state: Union[str, Interface]`) lose subclass identity through `model_dump()`. Keep the app entry point using `python://` strings to avoid this.

---

## Applications: canonical layout (`pyswark/apps/<name>/`)

Everything that **uses** the workflow framework lives under `pyswark/apps/`.
Use the `baseball` app as the reference implementation. The layout below is
deliberately verbose — it lets you scale out steps, workflows, runners, and
states independently, which is exactly what you need for data pipelines and
analytics where you'll be plugging in and swapping pieces.

```
pyswark/apps/<app_name>/
├── __init__.py
├── steps/           # Step model CLASSES — the compute. One concept per file.
│   ├── __init__.py
│   ├── extract.py   # e.g., ExtractModel
│   ├── transform.py # e.g., TransformModel
│   └── load.py
├── workflows/       # Workflow INSTANCES — named graphs of steps.
│   ├── __init__.py
│   └── etl.py       # WORKFLOW = Workflow(steps=[Step(...), Step(...)])
├── states/          # State FACTORIES — produce initial State for a scenario.
│   ├── __init__.py
│   └── season.py    # def create(year); SEASON_2023 = create(2023)
└── runner/          # Runner FACTORIES — wire workflow + state into a Runner.
    ├── __init__.py
    └── etl.py       # def create(year) -> Runner(workflow='python://...', state='python://...')
```

### What goes where

- **`steps/<name>.py`** — exactly one pydantic model with `run(self) -> dict`.
  Imports only from `pyswark.lib`, `pyswark.core`, and third-party libs.
  Contains the compute; knows nothing about state or workflows.

- **`workflows/<name>.py`** — module-level `WORKFLOW = Workflow(steps=[...])`.
  References step classes by `python://` path (dotted string) OR imports them
  directly. Step classes are composed here — never define a step model inside
  a workflow file. Multiple workflows (e.g., `etl.py`, `analysis.py`,
  `backfill.py`) coexist in this directory as independent named graphs.

- **`states/<name>.py`** — a `create(**kwargs)` factory returning a `State` or
  `StateWithGlueDb`, plus any module-level named instances (e.g.,
  `SEASON_2023 = create(2023)`). Factories encode "what inputs to feed this
  workflow for this scenario." One file per scenario family.

- **`runner/<name>.py`** — a `create(**kwargs)` factory returning a `Runner`
  wired with `python://` refs to a workflow and a state. This is the stable
  public entry point users import:

  ```python
  from mypkg.apps.<app_name>.runner import etl
  runner = etl.create(year=2023)
  result = runner.run()
  ```

### Why this scales

- **Add a new step** → drop a file in `steps/`. No other file changes. Reference it from whichever workflow needs it.
- **Try a new processing approach** → add `workflows/alternative.py` with a different step graph. Existing workflow untouched.
- **New scenario / dataset** → add a factory in `states/` and a thin wiring file in `runner/`. Flip between scenarios by swapping the state ref, not rewriting code.
- **A/B a different pipeline** → two runner factories pointing at two different workflows, same state factory. Compare results.
- **Loose coupling via `python://` refs** → the runner holds strings, not live objects. Module re-import on every `Runner.run()` means no hidden state leakage between runs.

### Reference implementation: `apps/baseball/`

```
apps/baseball/
├── steps/extract.py          # ExtractModel(uri: str) -> {'data': ...}
├── workflows/etl.py          # WORKFLOW = Workflow(steps=[Step(ExtractModel, ...)])
├── states/season.py          # create(year) -> StateWithGlueDb; SEASON_2023
└── runner/etl.py             # create(year) -> Runner(workflow='python://...', state='python://...')
```

User entry point:

```python
from pyswark.apps.baseball.runner import etl
runner = etl.create(2023)
runner.run()
runner.rerun()   # cache-safe idempotent rerun
```

### Testing a new app

Mirror the source tree under `pyswark/tests/unittests/apps/<app_name>/`:

- `test_steps_<name>.py` — instantiate the step's model and call `run()` directly on known inputs.
- `test_workflows_<name>.py` — build a small test state (usually `State`, not `StateWithGlueDb`, for speed), call `workflow.run(state)`, assert `stepsRan`, `stepsSkipped`, and the state contents after.
- `test_runner_<name>.py` — test the factory returns a `Runner` with the expected `python://` refs; optionally run a smoke test end-to-end.

For the framework itself, see existing tests in
`pyswark/tests/unittests/workflow/` (`test_workflow.py`, `test_runner.py`) —
they use a mixin pattern to exercise both `State` and `StateWithGlueDb`.

### Building a new app from scratch (checklist)

1. `mkdir -p pyswark/apps/<app>/{steps,workflows,states,runner}` and add empty `__init__.py` to each.
2. Write each compute unit as a `BaseModel` with a `run()` method in its own file under `steps/`. Test it in isolation first.
3. Compose steps into one or more `Workflow` instances under `workflows/<graph>.py`.
4. Write a state factory under `states/<scenario>.py` that produces the initial `State` / `StateWithGlueDb`.
5. Wire workflow + state into a `Runner` factory under `runner/<graph>.py` using `python://` refs.
6. Add tests under `pyswark/tests/unittests/apps/<app>/`.
7. **Do not** import across apps. If two apps need the same step, promote it to `pyswark/workflow/` or a shared library module.
