# Technical Debt Tracker

Items are graded by impact (how much they slow development) and effort (how much
work to fix). Address high-impact / low-effort items first.

## Active debt

| ID | Area | Description | Impact | Effort | Logged |
|----|------|-------------|--------|--------|--------|
| TD-001 | packaging | No `pyproject.toml`; relies on `setup.py` + `meta.yaml`. Modern tooling (pip, uv) expects pyproject.toml. | Medium | Medium | 2026-04 |
| TD-002 | core.io | Empty `__init__.py` files across subpackages make public API surface unclear; no `__all__` declarations. | Medium | Low | 2026-04 |
| TD-003 | tests | Integration tests require external service access (Google Drive, etc.) with no mock fallback. | Medium | Medium | 2026-04 |
| TD-004 | docs | Sphinx docs reference `autodoc` but some modules lack docstrings on public functions. | Low | Low | 2026-04 |
| TD-005 | lib.aenum | `aenum` is a niche dependency; evaluate whether stdlib `enum` extensions could replace it. | Low | High | 2026-04 |
| TD-006 | sekrets | Credential loading uses `python://` URI protocol, which is powerful but makes the call chain hard to trace for newcomers. | Low | Medium | 2026-04 |

## Resolved debt

| ID | Area | Description | Resolution | Date |
|----|------|-------------|------------|------|
| — | — | (none yet) | — | — |

## Process

1. When you encounter debt, add a row to the active table with a unique ID.
2. When creating a fix, reference the ID in your commit/PR message.
3. Move resolved items to the resolved table with a one-line resolution note.
