# Versioning

ArkheionX currently has two truths that must be kept separate:

- package/development version in this checkout;
- latest stable public release.

## Current package metadata

Live CLI output in this checkout reports:

```text
Arkheionx package version: 10.1.0.dev0
Latest stable release: v8.0.1
Current milestone: v10.1.0-dev
Next milestone: v10.1.0
```

The package metadata is defined in:

- `pyproject.toml`
- `arkheionx/version.py`

## Latest stable release

Latest stable release:

```text
v8.0.1
```

`v8.0.1` is the stable public release marker used by current version metadata.

## Current development branch

Current local branch during this session:

```text
private/v10-godeye-war-engine
```

This branch includes unreleased development work. It should not be described as the latest stable public release.

## What V10 means

V10 refers to experimental local development work in this checkout. Some V10 docs and CLI commands use internal codenames such as `war-run` or `GodEye`.

Public positioning should not use internal codenames as hero language.

Use:

```text
ArkheionX local-first review infrastructure
```

Do not use:

```text
AI auditor
exploit generator
automatic vulnerability finder
```

## Public/stable vs experimental/internal

| area | status |
|---|---|
| `arkheionx version` and `arkheionx doctor` | stable utility commands |
| `arkheionx review` | current primary review-pack workflow |
| `arkheionx review-map` and focused views | stable compact mapping workflow |
| legacy scanner/report commands | advanced/legacy |
| `hunter`, `war-run`, `memory`, `triage` | experimental/local-first |
| V10/GodEye docs | internal or historical unless explicitly promoted later |
| case-study and external-validation docs | public credibility layer |

## Release language

Allowed:

- "Latest stable release is v8.0.1."
- "This checkout includes unreleased development work."
- "V10.1 is a development milestone."

Avoid:

- "V10.1 is the stable public release."
- "The development branch is enterprise-ready."
- "Experimental commands are production validated."

## Validation

Use:

```bash
python3 -m arkheionx.cli.main version
grep -R "__version__\\|version =" -n arkheionx pyproject.toml
```

If docs, metadata, and CLI disagree, document the disagreement honestly before release.
