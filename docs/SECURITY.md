# Security

## Credential management

### Sekrets module

pyswark's `sekrets` module provides centralized credential management:

- Credentials are stored as typed GlueDb records in a local hub file
- Each credential is associated with a named protocol (e.g., `github-io-demo`, GDrive)
- Resolution: `sekrets.api.get(protocol_name)` → hub lookup → protocol-specific model
- The hub file location is configured via settings, not hardcoded

### Key principles

1. **Credentials never appear in source code.** Use sekrets or environment variables.
2. **Credentials never appear in committed files.** `.gluedb` hub files containing
   secrets must be in `.gitignore`.
3. **Typed credentials over raw strings.** Protocol models validate credential
   structure at load time, catching misconfiguration early.
4. **Credential indirection.** URIs use `@username` patterns that resolve at runtime
   via `core.fsspec.fix`, keeping actual secrets out of data pipeline code.

### fsspec credential injection

The `core.fsspec.fix` module intercepts fsspec calls:

```
URI: gdrive2://@myaccount/path/file.csv
  → fix.open() parses @myaccount
    → sekrets.api.get("myaccount")
      → Returns credential kwargs
        → Merged into fsspec.open() call
```

This keeps credential resolution transparent to handler code.

## Code execution risks

### `python://` URI scheme

The `python://` scheme uses `pydoc.locate` to import and return arbitrary Python
objects. This is powerful but carries inherent risk:

- **Only use with trusted URI sources.** A malicious `python://` URI could execute
  arbitrary code.
- **Do not expose `api.read()` to untrusted user input** without URI validation.
- This is acceptable for a personal utility library where the user controls all URIs.

### `pydoc.locate` in registries

`DataHandler` and other registries resolve import paths via `pydoc.locate`. These
paths are hardcoded in enum definitions within the codebase, so they are not a
runtime injection vector. However:

- Do not allow user input to set registry values
- Do not dynamically construct handler import paths from external data

## Dependency security

### Supply chain

- pyswark depends on well-known packages (numpy, pandas, pydantic, sqlmodel, fsspec)
- Distribution is via conda (`pyt3r` channel) — the channel is controlled by the author
- No automatic dependency updates; versions are pinned in `meta.yaml`

### Recommendations

1. Periodically audit dependencies for known vulnerabilities
2. Pin dependency versions in CI environments (already done via `ci/*.yml`)
3. Review new dependencies before adding them to `meta.yaml`

## Data handling

### Local data

- GlueDb catalogs are local JSON files; no network exposure
- File permissions are inherited from the filesystem; pyswark does not set permissions

### Remote data

- HTTP/HTTPS access via `requests`/`aiohttp` — standard TLS verification applies
- fsspec remote filesystems (S3, GDrive, etc.) — security depends on the fsspec
  implementation and credential configuration
- No custom TLS or certificate handling in pyswark

## Secrets in CI

- CI environment files (`ci/*.yml`) should never contain credentials
- Integration tests requiring credentials should be gated or use mock fixtures
- The `htmlcov/` directory (test coverage output) should be gitignored

## Security checklist for PRs

- [ ] No credentials, tokens, or secrets in committed files
- [ ] No new `python://` URIs with untrusted sources
- [ ] New dependencies reviewed for security posture
- [ ] Sekrets hub files remain in `.gitignore`
- [ ] No hardcoded file paths that could leak directory structure
