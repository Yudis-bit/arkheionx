# Public Docs Risk Inventory

| path | classification | risk | recommended action |
|---|---|---|---|
| `docs/` | public-safe | Large directory with many specialized docs; can overwhelm new readers. | Keep canonical entry in `docs/README.md`; keep specialized docs out of primary navigation unless current. |
| `docs/archive/` | archive | Low risk if clearly marked; already contains historical version and legacy workflow docs. | Keep. Use for historical docs when links/tests allow moves. |
| `docs/business/` | business | Can make a technical security repo look sales-first or service-first. Tests and workflows still reference these paths. | Keep in place for now; add boundary README; do not list as canonical technical docs. |
| `docs/marketing/` | marketing | Can look like growth-hacking material in a security repo. Tests/workflows reference `BRAND.md` and other files. | Keep in place for now; add boundary README; consider moving to `metadata/marketing/` after tests are updated. |
| `docs/private/` | internal | The word "private" inside a public repo is confusing and can imply accidental leakage. | Keep in place for now; add boundary README explaining no secrets belong here; consider `notes/internal/` or archive move later. |
| `docs/launch/` | historical | Launch planning is not core technical documentation and includes dated public-surface plans. Tests and metadata reference it. | Keep in place for now; add boundary README; consider archive move after tests/workflows are updated. |
| `docs/ecosystem/` | public-safe with boundaries | Useful for pilots and ecosystem validation, but can be misread as endorsement or formal grant status. | Keep; add boundary README emphasizing pilots/feedback, not endorsement. |
| `docs/internal/` | internal | Internal mode notes can be mistaken for stable public behavior. | Keep; add boundary README; do not expose in canonical docs navigation. |
| `docs/papers/` | historical/reference | Fine if clearly historical; generated HTML/PDF may carry old repo URLs. | Keep; retain `README.md`; update generated artifacts only during a deliberate publication pass. |
| `docs/releases/` | historical/reference | Useful release history; can be noisy but legitimate. | Keep; optional README boundary if release docs expand further. |
| `docs/templates/` | public-safe | Reusable templates are acceptable, but should not be confused with CLI output. | Keep. |
| `docs/case-studies/` | canonical public | New credibility path; must avoid acceptance claims without proof. | Keep; continue using template and outcome language. |

## Reference findings

`docs/business`, `docs/marketing`, `docs/private`, and `docs/launch` are referenced by tests, workflows, scripts, metadata, or existing docs. Moving them now would create broad link and test churn. The safer Phase 2 cleanup is boundary documentation and canonical-navigation restraint.

