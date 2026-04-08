# Core Beliefs

**Status:** Active
**Last verified:** 2026-04

These are the operating principles that govern how agents (and humans) should
make decisions when working in this codebase. When in doubt, refer here.

---

## 1. Layers are load-bearing walls

The dependency direction `lib → core → application` is not a suggestion — it is the
primary structural invariant. Every import must flow forward through the layers.
Violations compound into circular dependencies and make the codebase illegible to
future agent runs.

**Enforcement:** Review all new imports. If a core module needs something from an
application package, the abstraction is in the wrong layer — refactor it downward.

## 2. URIs are the universal address

All data is addressed by URI. The I/O framework routes on scheme and extension,
not on ad-hoc file path manipulation. When adding new data sources, register a
handler — do not add one-off read logic.

## 3. Registries over conditionals

Prefer `AliasEnum` registries and `pydoc.locate` resolution over `if/elif` chains.
Registries are discoverable, extensible, and self-documenting. New formats and
schemes should be added by registering, not by branching.

## 4. Pydantic is the contract layer

Configuration, DTOs, extractors, handlers, and workflow state are all Pydantic models.
This gives us validation at boundaries, serialization for free, and a consistent
mental model. Do not introduce raw dicts where a model would clarify intent.

## 5. Single source of truth for metadata

Version, dependencies, and entry points live in `conda-recipe/meta.yaml`. `setup.py`
and Sphinx `conf.py` read from it. Never duplicate this information.

## 6. Boring technology, composed well

Prefer stable, well-documented dependencies that agents can reason about from
training data and in-repo docs. When an external library is opaque or unstable,
consider reimplementing the needed subset with full test coverage.

## 7. Validate at boundaries, trust inside

Data entering the system (from URIs, user input, external APIs) must be validated
— via Pydantic parsing, schema checks, or explicit guards. Once inside a trusted
layer, avoid redundant defensive checks that obscure logic.

## 8. Tests are executable documentation

Every public function and handler should have tests that demonstrate correct usage.
Tests are often the first thing an agent reads to understand a module. Write them
to be legible, not just correct.

## 9. Documentation lives in the repo

If a decision, pattern, or constraint is not discoverable from the repository itself,
it effectively does not exist for agents. Slack threads, mental models, and verbal
agreements must be encoded as markdown, code comments, or linter rules.

## 10. Small, frequent improvements over big rewrites

Technical debt is paid down continuously. When you encounter a suboptimal pattern,
fix it locally or log it in `exec-plans/tech-debt-tracker.md`. Do not let debt
compound silently.
