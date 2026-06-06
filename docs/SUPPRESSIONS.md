# Suppressions

Suppressions document a decision to keep a known readiness signal out of the
active finding set for a specific run. They do not prove safety.

```json
{
  "id": "ARK-VLT-001",
  "path": "src/",
  "reason": "Tracked in remediation issue #42.",
  "expires": "2026-12-31",
  "owner": "security-lead",
  "review_after": "2026-06-30"
}
```

Required fields:

- `id`
- `reason`

Optional fields:

- `path`
- `expires`
- `owner`
- `review_after`

Suppressed findings remain visible in Markdown and JSON under suppressed
sections. They should be reviewed before launch, audit intake, contest prep, or
bug bounty readiness.

## Rules

- Use stable Arkheionx finding IDs or prefixes.
- Include a clear reason.
- Prefer an expiration or review date.
- Do not suppress a finding to create a launch claim.
- Re-run Arkheionx after remediation and remove stale suppressions.
