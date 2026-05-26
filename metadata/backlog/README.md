# PoC Backlog

This directory tracks **candidate** incidents that may eventually become
verified entries in `metadata/registry.json`. Candidates here are not
PoCs. They are the queue.

The backlog is the input to the [intake pipeline](../../docs/INCIDENT_INTAKE.md).

## Layout

```
metadata/backlog/
├── README.md                       # this file
├── candidates.template.json        # schema-by-example for one candidate
└── candidates/                     # one file per candidate, <id>.json
```

A candidate file is a single JSON object using the fields documented in
`candidates.template.json`.

## Candidate lifecycle

```
candidate
   |
   v
metadata-drafted
   |
   v
poc-in-progress
   |
   v
compiles  --->  assertions-added  --->  fork-verified  --->  published
                                                                  ^
                                                                  |
                                            (entry promoted into registry.json
                                             and verification report committed)
```

A candidate may also reach `rejected` for any of:

- Live-target only / no defensive value.
- Insufficient public sources to write an honest entry.
- Duplicate of an existing entry.
- Embargoed and unlikely to clear soon.

## Adding a candidate

1. Pick a stable `candidate_id`. Convention: `<YYYY-MM>-<protocol-slug>`,
   matching what the registry id will be if this candidate publishes.
2. Copy `candidates.template.json` to `candidates/<candidate_id>.json`.
3. Fill required fields. Leave unknown values as `null` rather than
   inventing a guess.
4. Open a PR describing why this incident is worth the slot.

## What does NOT belong here

- Entries that are already in `metadata/registry.json`.
- Vague "I heard about a hack on X" without a public source.
- Targets that are still vulnerable in production (those go through the
  embargo path, not the public backlog).
- 100 fake placeholder entries to make the queue look longer.

## Why a backlog at all

At small scale, candidates can live in someone's notes. Past 25 entries,
they need to be tracked: which incidents have been triaged, which were
rejected and why, which are blocked on archival RPC, which are blocked
on taxonomy review. The backlog is the place that record lives.

It is sized to the goals in [`docs/launch/EXPANSION_PLAN.md`](../../docs/launch/EXPANSION_PLAN.md).
The structure is the system that needs to be ready before mass intake;
the entries themselves are added one at a time, with sources.
