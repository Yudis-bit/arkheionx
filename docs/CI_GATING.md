# CI Gating

Arkheionx is non-blocking by default. Indie builders should be able to install
the GitHub Action without immediately breaking CI.

v0.4.0 adds explicit threshold flags for teams that want readiness gates.

## Available Gates

| Flag | Behavior |
|---|---|
| `--fail-score-below N` | Fails when readiness score is below `N`. |
| `--fail-on-new-high` | Fails when baseline diff mode finds new high or critical readiness gaps. |
| `--fail-on-unsuppressed-high` | Fails when the current scan has unsuppressed high or critical readiness gaps. |
| `--fail-on-critical-readiness-gap` | Existing strict gate for critical readiness gaps. |

All gates are disabled unless explicitly enabled.

## Recommended For Indie Builders

Start with reports only:

```yaml
with:
  protocol-type: "auto"
  json-output: "arkheionx-report.json"
  sarif-output: "arkheionx.sarif.json"
```

After the report becomes part of team workflow, add a score threshold:

```yaml
with:
  fail-score-below: "60"
```

## Recommended For Mature Teams

Once the team has a baseline:

```yaml
with:
  compare-baseline: "arkheionx.baseline.json"
  fail-on-new-high: "true"
```

This blocks newly introduced high/critical readiness gaps while allowing the
team to work down existing findings.

## Caution

Threshold failures are readiness gates. They are not vulnerability
confirmations and should be reviewed with context. False positives should be
reported through the False Positive Report issue template.

v0.6.0 confidence reasons and detection sources make gates easier to review.
For early teams, prefer score thresholds or `fail-on-new-high` over blocking on
all high gaps. Low-confidence keyword-only findings should usually be reviewed
before they become CI blockers.
