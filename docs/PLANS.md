# Plans & Roadmap

## Current focus areas

### Near-term (active)

1. **Documentation completeness** — Ensure all public modules have docstrings
   compatible with Sphinx autodoc. Tracked in `QUALITY_SCORE.md`.

2. **Modernize packaging** — Add `pyproject.toml` as the primary metadata source
   while maintaining conda-build compatibility. See `references/uv-llms.txt` and
   tech debt TD-001.

3. **Public API clarity** — Add `__all__` declarations to key `__init__.py` files
   so the importable surface is explicit. Tech debt TD-002.

### Medium-term

4. **Test isolation** — Create mock/fixture alternatives for integration tests that
   require external services (Google Drive, HTTP endpoints). Tech debt TD-003.

5. **GlueDb enhancements** — Support for record versioning, diff/merge between
   catalogs, and richer query expressions via the `query` module.

6. **Workflow improvements** — Better step dependency graphs, parallel execution
   support, and integration with GlueDb for artifact tracking.

### Longer-term

7. **Plugin system** — Allow third-party packages to register handlers, URI schemes,
   and GlueDb model types without modifying pyswark source.

8. **CLI expansion** — Beyond the current `pyswark-entry-point`, provide CLI commands
   for common operations: `pyswark read <uri>`, `pyswark gluedb list <db>`, etc.

9. **Async I/O** — The `aiohttp` dependency is already present; expose async
   variants of `api.read()` / `api.write()` for high-throughput pipelines.

## Execution plans

Active and completed execution plans for complex work items live in:
- `exec-plans/active/` — work in progress
- `exec-plans/completed/` — done, kept for decision history

Technical debt is tracked separately in `exec-plans/tech-debt-tracker.md`.

## How to create an execution plan

For any task that spans more than a single PR:

1. Create a `.md` file in `exec-plans/active/` named `YYYY-MM-DD-short-title.md`
2. Include: goal, approach, decision log, progress checklist
3. Reference the plan in relevant PR descriptions
4. When complete, move to `exec-plans/completed/` with a summary

## Decision log format

Within an execution plan, log decisions as they happen:

```markdown
### Decision: [topic]
**Date:** YYYY-MM-DD
**Options considered:** A, B, C
**Chosen:** B
**Rationale:** [why]
```
