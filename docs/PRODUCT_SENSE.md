# Product Sense

## What pyswark is

pyswark is a **personal Python utility library** — a "swiss army knife" for data
practitioners who want unified I/O, lightweight data cataloging, and reproducible
workflows without the overhead of enterprise tooling.

## Who it serves

### Primary user: the author (pyt3r)

pyswark was built to solve the author's own pain points in analytical and data
engineering workflows. It reflects personal preferences and workflow patterns,
which means:

- It prioritizes ergonomics for a single power user over broad adoption
- New features arise from real workflow friction, not speculative demand
- The library surface reflects one person's needs, not a committee design

### Secondary users: Python data practitioners

Developers with similar workflows (read data from various sources, catalog artifacts,
chain transformations, manage credentials) can benefit from pyswark's approach. The
blog posts on pyt3r.github.io serve as the primary outreach channel.

## Core value propositions

### 1. "One import, any source"

`api.read(uri)` works for local files, HTTP resources, Python objects, packaged
assets, and credential-protected remote filesystems. Users don't need to remember
which library to import for which source.

### 2. "Track your artifacts without a server"

GlueDb provides catalog management in a single `.gluedb` file. No database server,
no cloud service, no setup. Portable, version-controllable, and queryable.

### 3. "Credentials that just work"

Sekrets + fsspec integration means URIs like `gdrive2://@myaccount/path/file.csv`
resolve credentials automatically. No env var juggling per session.

### 4. "Reproducible pipelines, locally"

The Workflow module caches step outputs and skips completed work. Designed for
iterative analytical workflows where you re-run frequently during development.

## Product positioning

| Dimension | pyswark | Alternatives |
|-----------|---------|-------------|
| **I/O** | URI-dispatched, registry-based | `pandas.read_*`, `fsspec.open()` directly |
| **Cataloging** | GlueDb: file-based, no server | DVC, MLflow, Hive metastore |
| **Credentials** | Sekrets: typed, hub-resolved | env vars, .env files, cloud secret managers |
| **Workflow** | Cached steps, local | Prefect, Airflow, Luigi |
| **Scope** | Personal toolkit, opinionated | General-purpose, configurable |

pyswark is not trying to replace these tools at scale. It fills the gap for personal
and small-team workflows where the alternatives are either too heavy or too scattered.

## User feedback channels

- Blog posts on pyt3r.github.io (comments, if enabled) — see `docs/BLOG_POSTS.md` for index
- GitHub issues on pyt3r/pyswark and pyt3r/pyswark-lib
- Direct usage observation (the author is the primary user)

## Product principles

1. **Solve real friction** — only add features that address actual workflow pain
2. **Stay lightweight** — no server processes, no cloud dependencies for core functionality
3. **Be composable** — modules should work independently, not just as a monolith
4. **Eat your own cooking** — the author uses every feature in real workflows
