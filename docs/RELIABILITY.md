# Reliability

## Testing strategy

### Unit tests

Located in `pyswark/tests/unittests/`. Run with:

```bash
make test
```

Coverage is collected via `coverage` (included as a runtime dependency in meta.yaml).

Unit tests should:
- Be fast (no network, no filesystem side effects)
- Test one behavior per test function
- Use descriptive names that explain the scenario
- Mock external dependencies (fsspec, HTTP, file I/O) where needed

### Integration tests

Located in `pyswark/tests/integration/`. These test real I/O paths:
- Local file read/write cycles
- GlueDb persistence round-trips
- Sekrets credential resolution (requires credentials on disk)
- fsspec remote filesystem access (requires network + credentials)

Integration tests are not run in CI by default if they require external services.
See tech debt TD-003 for mock fallback plans.

### Example scripts

Examples in `examples/` are runnable scripts and sphinx-gallery sources. They serve
as both documentation and smoke tests. Sphinx-gallery executes them during doc builds,
providing a passive regression check.

## Error handling patterns

### Boundary validation

Data entering the system is validated at the boundary:
- `UriModel` validates URI structure on construction
- `IoHandler` validates handler selection before dispatch
- Pydantic models reject invalid data at parse time
- GlueDb enforces unique record names

### Fail-fast philosophy

pyswark prefers raising clear exceptions early over silently degrading:
- Unknown URI schemes → `ValueError` with message naming the scheme
- Missing handlers → clear error from `DataHandler.get()`
- Invalid credentials → exception from sekrets before fsspec attempt

### Logging

`util.log` provides structured logging for I/O operations. The `Log.decorate`
decorator in `core.io.decorate` adds entry/exit logging with URI and handler info.
Verbosity is controlled via `api.setVerbosity()`.

## Known reliability concerns

| Area | Concern | Mitigation |
|------|---------|-----------|
| `core.fsspec.fix` | Credential injection is implicit; failures surface as opaque fsspec errors | Improve error messages; add pre-flight credential validation |
| `python://` URIs | Arbitrary code execution via `pydoc.locate` | Only use with trusted URI sources; document the risk |
| GlueDb persistence | No file locking; concurrent writes can corrupt | Single-user library; document as non-concurrent |
| Workflow caching | Cache invalidation relies on input fingerprinting; hash collisions possible | Extremely unlikely with current data sizes |

## Observability

pyswark is a library, not a service, so observability is lightweight:

- **Logging:** via `util.log`, controllable per-operation verbosity
- **Test coverage:** collected by `make test`, viewable in `htmlcov/`
- **Sphinx-gallery:** example execution during doc builds catches regressions

## Incident response

For a personal library, "incidents" are typically:
1. A test failure after a change — fix the test or the code, not the test
2. A broken example — update the example to match current API
3. A credential error — check sekrets hub configuration
4. A dependency breakage — pin the dependency version in meta.yaml
