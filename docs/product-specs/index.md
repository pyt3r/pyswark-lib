# Product Specs — Index

Product specifications describe user-facing capabilities: what the feature does,
who it serves, and how success is measured. They are the bridge between product
vision and implementation work.

## Catalog

| Spec | Domain | Status | Last updated |
|------|--------|--------|-------------|
| [new-user-onboarding.md](new-user-onboarding.md) | All | Active | 2026-04 |

## Adding a new spec

1. Create a new `.md` file in this directory.
2. Use the template below.
3. Add an entry to the catalog table above.

### Template

```markdown
# [Feature Name]

**Status:** Draft | Active | Shipped | Deprecated
**Owner:** [name]
**Date:** [YYYY-MM-DD]

## Problem

What user problem does this solve?

## Users

Who benefits and in what context?

## Solution

High-level description of the feature.

## Success criteria

How do we know this is working?

## Non-goals

What this feature explicitly does not do.

## Dependencies

What must exist before this can be built?
```
