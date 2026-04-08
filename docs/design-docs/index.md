# Design Documents — Index

This directory catalogs architectural and design decisions for pyswark.
Each document captures the reasoning behind a significant choice, its status,
and any open questions.

## Catalog

| Document | Domain | Status | Last verified |
|----------|--------|--------|---------------|
| [core-beliefs.md](core-beliefs.md) | All | ✅ Active | 2026-04 |
| [../DESIGN.md](../DESIGN.md) | Architecture | ✅ Active | 2026-04 |

## Verification

Design docs should be reviewed quarterly to confirm they still reflect actual
codebase behavior. When a document becomes stale:

1. Update it to match current reality, or
2. Move it to a `deprecated/` subdirectory with a note explaining why.

## Adding a new design doc

1. Create a new `.md` file in this directory.
2. Use the template below.
3. Add an entry to the catalog table above.

### Template

```markdown
# [Title]

**Status:** Draft | Active | Deprecated
**Author:** [name]
**Date:** [YYYY-MM-DD]
**Last verified:** [YYYY-MM-DD]

## Context

Why this decision was needed.

## Decision

What was decided and why.

## Consequences

What follows from this decision — tradeoffs, constraints, follow-up work.

## Open questions

Anything unresolved.
```
