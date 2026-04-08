# Quality Score

This document grades each module across key quality dimensions. Grades are
updated as improvements land. Use this to identify where to invest effort.

## Grading scale

- **A** — Excellent: well-documented, well-tested, clean API
- **B** — Good: functional, reasonable coverage, minor gaps
- **C** — Adequate: works but has notable gaps in docs, tests, or API clarity
- **D** — Needs work: significant gaps that affect usability or maintainability
- **F** — Critical: broken, untested, or fundamentally unclear

## Module grades

| Module | Tests | Docs | API clarity | Overall | Notes |
|--------|-------|------|-------------|---------|-------|
| `lib.pydantic.base` | B | B | A | B | Good foundation; docstrings could be richer |
| `lib.pydantic.ser_des` | B | B | B | B | Blog post explains well; in-code docs adequate |
| `lib.aenum` | B | C | B | B- | Niche dependency; docs assume familiarity with aenum |
| `lib.enum` | B | C | B | B- | Thin wrapper; documentation minimal |
| `lib.fsspec` | C | C | C | C | Registration logic not well documented |
| `core.io.api` | B | B | A | B+ | Main public surface; well-structured |
| `core.io.iohandler` | B | C | B | B- | Internal; docs could explain flow better |
| `core.io.guess` | B | C | B | B- | Enum-based guessing works but edge cases unclear |
| `core.io.datahandler` | B | C | B | B- | Registry pattern clear; docs sparse |
| `core.io.base` | B | C | B | B- | AbstractDataHandler contract could be better documented |
| `core.io.decorate` | C | D | C | C | Decorator behavior not well explained |
| `core.io.{format handlers}` | B | C | B | B- | Individual handlers vary in completeness |
| `core.models.uri` | B | C | B | B- | Pluggable but registration docs thin |
| `core.models.db` | B | C | B | B- | MixinDb pattern powerful but dense |
| `core.extractor` | B | C | B | B- | Base class; docs could show usage patterns |
| `core.fsspec` | C | D | C | C | fix.py credential injection not well documented |
| `gluedb` | B | B | B | B | Blog post + getting_started cover well |
| `sekrets` | C | C | C | C | Blog post helps; in-code docs sparse; setup UX unclear |
| `workflow` | C | C | C | C | Concept clear; caching behavior under-documented |
| `tensor` | C | C | C | C | Numpy wrappers; usage patterns not obvious |
| `ts` | B | C | B | B- | TsVector useful; DatetimeList well-covered in tutorial |
| `query` | C | D | C | C- | Multiple backends; not clear which to use when |
| `util.log` | C | D | C | C | Internal utility; minimal docs |
| `infra` | C | D | C | C | Build machinery; not user-facing |

## Summary

| Grade | Count | Percentage |
|-------|-------|------------|
| A     | 0     | 0%         |
| B+    | 1     | 4%         |
| B     | 4     | 17%        |
| B-    | 8     | 35%        |
| C     | 7     | 30%        |
| C-    | 1     | 4%         |
| D     | 0     | 0%         |
| F     | 0     | 0%         |

**Overall library grade: B-**

## Priority improvements

1. **Documentation** is the weakest dimension across the board. Adding docstrings
   to public functions in `core.io`, `core.fsspec`, and `sekrets` would move
   multiple modules from C to B.

2. **API clarity** for `query` — the module has multiple backends (dataframe, model,
   native) with no guidance on when to use which.

3. **Test coverage** for `core.fsspec.fix` and `sekrets` — credential paths are
   hard to test but high-impact when they break.

## Tracking changes

When you improve a module's quality, update the grade here with a brief note.
Include the date and what changed:

```
| `sekrets` | C→B | C→B | C→B | C→B | 2026-04: added docstrings, fixture-based tests |
```
