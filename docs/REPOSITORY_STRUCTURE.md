# Repository Structure

ArkheionX is organized as a local-first review workbench, not as an exploit dump.

- `arkheionx/` - Python package and CLI implementation.
- `docs/` - public documentation and deeper references.
- `docs/archive/` - historical docs, not the current public entry point.
- `examples/` - demo fixtures and expected output examples.
- `artifacts/` - generated smoke-test or sample artifacts; contents are ignored except for the boundary README.
- `schemas/` - JSON schemas for generated outputs.
- `site/` - Astro website source.
- `metadata/` - positioning, feedback, registry, search, and ecosystem metadata.
- `templates/` - reusable review, scope, feedback, and case-study templates.
- `reports/` - generated indexes and historical verification reports.
- `EVM/`, `MoveVM/`, `SVM/` - historical vulnerable-case and VM validation fixtures. These paths are kept stable for tests and metadata, but they are not live exploit tooling.
- `notes/` - local maintainer notes and cleanup reports.
- `.github/` - workflows, actions, issue templates, and repository contribution surface.

## Local generated directories

Local runs may create `.arkheionx/`, `site/dist/`, `site/.astro/`, `build/`, `dist/`, `*.egg-info`, `__pycache__/`, and `.pytest_cache/`. These are not the public source of truth unless explicitly packaged.

`site/node_modules/` is a local dependency directory for the website and should not be committed.

## Public reading order

Start with:

1. [`README.md`](../README.md)
2. [`docs/README.md`](README.md)
3. [`docs/START_HERE.md`](START_HERE.md)
4. [`docs/WHAT_IS_ARKHEIONX.md`](WHAT_IS_ARKHEIONX.md)
5. [`docs/WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md)

Specialized folders such as `docs/business/`, `docs/marketing/`, `docs/private/`, and `docs/launch/` are intentionally not the main technical entry point.

