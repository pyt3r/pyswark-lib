# Blog Posts — pyt3r.github.io

These posts are the primary long-form documentation for pyswark's design decisions
and module patterns. When working on a module, read the relevant post first — it
often explains the *why* more clearly than in-code comments do.

All posts live at: https://pyt3r.github.io

## Posts by module

| Post | Module(s) covered | Key ideas |
|------|-------------------|-----------|
| [How I Organize Python Libraries](https://pyt3r.github.io/how-i-organize-python-libraries/) | All — `lib/`, `core/`, application packages | Layer model, dependency direction, `lib` rule |
| [Upgrade constants.py with AliasEnum](https://pyt3r.github.io/upgrade-constants-py-with-alias-enum/) | `lib.aenum` | `AliasEnum`, `Alias`, registry pattern |
| [Pydantic Serialization](https://pyt3r.github.io/pydantic-serialization/) | `lib.pydantic.ser_des` | Type-preserving JSON (`toJson` / `fromJson`), embedded model paths |
| [Intro to GlueDb](https://pyt3r.github.io/intro-to-gluedb/) | `gluedb` | Catalog design, `Db`, `Hub`, `.gluedb` file format |
| [fsspec + Google Drive Service Account](https://pyt3r.github.io/fsspec-google-drive-service-account/) | `core.fsspec`, `sekrets` | GDrive service account setup, fsspec integration |
| [Managing Credentials with pyswark Sekrets](https://pyt3r.github.io/managing-credentials-with-pyswark-sekrets/) | `sekrets` | Hub setup, `sekrets.api.get()`, credential indirection |
| [Build Python Code](https://pyt3r.github.io/build-python-code/) | General | Python packaging patterns, entry points |

## Notes for agents

- These posts are external (GitHub Pages) and not versioned with the library.
- When a post contradicts in-repo docs, **in-repo docs take precedence**.
- When adding a new module or changing public API, consider whether an existing
  post needs an update or a new post is warranted. Note this in the relevant
  execution plan.
