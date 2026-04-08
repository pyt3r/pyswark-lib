# Design Principles

## Philosophy

pyswark is a personal utility library designed to be a "swiss army knife" for Python
workflows involving data I/O, serialization, cataloging, and orchestration. It favors:

- **Composability** over monolithic features
- **URI-addressed everything** over file-path spaghetti
- **Explicit registries** over implicit magic
- **Layered architecture** over flat utility dumps

## Core design decisions

### 1. URI as the universal interface

Every data source — local files, HTTP endpoints, Python objects, packaged assets,
remote filesystems — is addressed by a URI string. The I/O framework dispatches on
scheme and extension to the appropriate handler. This means:

- `api.read("data.csv")` and `api.read("https://example.com/data.csv")` use the
  same call site
- `api.read("python://mymodule.MyClass")` imports a Python object
- `api.read("pyswark://data/x.yaml")` reads from packaged assets

### 2. Registry-driven extensibility

New formats, schemes, and protocols are added by registering enum members, not by
modifying switch statements. `AliasEnum` maps names to import paths; `pydoc.locate`
does lazy resolution. This keeps the core framework closed for modification but open
for extension.

### 3. Pydantic as the contract boundary

All structured data crossing module boundaries is a Pydantic model. This gives:
- Automatic validation at ingress
- JSON serialization
- Self-documenting schemas
- IDE support via type annotations

The `ser_des` module adds type-preserving round-trips: `toJson(model)` embeds the
model's import path so `fromJson(blob)` can reconstruct the exact type.

### 4. GlueDb as lightweight catalog

GlueDb fills the gap between "just use files" and "set up a database server."
It stores named records (often URIs to artifacts) in a portable `.gluedb` JSON file,
with optional SQLModel views for querying. Born from personal analytics workflows
where tracking files, models, and configs became unwieldy.

### 5. Sekrets as credential indirection

Rather than env vars scattered across `.bashrc` files, Sekrets stores typed credentials
in a GlueDb hub, resolved by protocol name. The fsspec integration layer (`core.fsspec.fix`)
intercepts `@username` URI patterns and injects the right credentials transparently.

### 6. Workflow as cached pipelines

The Workflow module provides multi-step pipelines where each Step has typed inputs and
outputs. The caching mechanism (Extracts) fingerprints inputs to skip completed steps.
Designed for reproducible analytical workflows, not general job orchestration.

## Design anti-patterns to avoid

- **Circular imports** — the layer model exists to prevent this; never import upward
- **God modules** — if a file exceeds ~300 lines, it likely needs decomposition
- **Raw dicts at boundaries** — use Pydantic models instead
- **One-off read/write logic** — register a handler instead
- **Hardcoded paths** — use URIs and the I/O framework
