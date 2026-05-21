# Reproducibility Standard

This document defines the reproducibility statuses used in
`metadata/registry.json` and what each one promises. The bar matters: a
"deterministic-confirmed" entry should mean what it says.

---

## Statuses

### `deterministic-confirmed`

The PoC has been executed against the declared fork block on the
declared chain alias, all required assertions pass, and a verification
report exists at `reports/verification/<id>.md` produced by
`scripts/generate_verification_report.py` (or recorded manually with the
same fields).

**Required.**
- Fork block pinned in the test file.
- RPC alias declared and resolvable.
- All assertions in [ASSERTION_STANDARD.md](ASSERTION_STANDARD.md) for
  the entry's category pass.
- A verification report dated within the last reasonable time window
  (re-verify on schema or library changes).

This is the only status that may be cited as "verified" in summaries.

### `deterministic-likely-but-unverified`

The PoC compiles, the logic looks sound, the block / chain are correct,
and the assertions look right — but the fork test has not been run end
to end in the current environment.

**Required.**
- Code compiles.
- Block and alias declared.
- Assertions present and category-appropriate.

**Forbidden.**
- Calling this status "verified".
- Using this status to inflate counts.

This is the default for entries inherited without execution evidence.

### `requires-archival-rpc`

The PoC needs an archival RPC (e.g. for very old blocks, or for
non-mainnet chains where consumer RPCs prune state) and that RPC is not
configured in the local environment.

**Required.**
- Same code-level standards as `deterministic-likely-but-unverified`.
- A clear statement of what RPC capability is missing (archival depth,
  trace support, debug namespace).

This status is honest about *why* verification has not happened. It is
not a synonym for "we never tried".

### `partially-reproducible`

Some but not all parts of the exploit reproduce. Common cases: the
funding leg reproduces but the final state-change does not, or the
reproduction depends on contract code that has been redeployed /
self-destructed since the incident.

**Required.**
- `notes` field describes which parts reproduce and which do not.
- A linked reference to the upstream PoC, post-mortem, or report that
  documents the original chain trace.

### `compile-only`

The PoC builds under `forge build` but is not executable end to end.
Useful for incidents where the contracts themselves illustrate the bug
even if a fork run is not feasible.

**Required.**
- A `notes` entry explaining why fork execution is not feasible.
- All claims in `summary` / `root_cause` / `impact` sourced to
  references.

### `incomplete`

The PoC has known gaps marked by the original author. Listed in the
archive for traceability, not as a finished artifact.

**Required.**
- `notes` field enumerates the gaps.
- `status` should also be `incomplete`.

### `unknown`

The PoC is in the archive but its reproducibility has not been assessed
yet. Should be transient — `unknown` entries are triaged in the next
backlog grooming pass.

---

## Promotion path

A PoC moves through these statuses in roughly this order:

```
unknown
   |
   v
incomplete  ----->  compile-only  ----->  deterministic-likely-but-unverified
                                                    |
                                                    v
                                          requires-archival-rpc (if RPC missing)
                                                    |
                                                    v
                                          deterministic-confirmed
```

Promotion to `deterministic-confirmed` requires:

1. A successful run on the declared fork block with the declared alias.
2. All category-required assertions passing.
3. A verification report committed at `reports/verification/<id>.md`.
4. A maintainer signoff on the PR that flips the status.

Demotion happens automatically:

- A library / submodule update that breaks compilation drops the entry
  to `compile-only` until rebuilt.
- A change to the assertion standard that adds a required assertion the
  entry does not yet satisfy drops it to
  `deterministic-likely-but-unverified` until updated.

---

## Honesty rules

- An entry's `reproducibility` field must reflect the *actual* state of
  the PoC in the current commit. Do not carry forward optimistic
  statuses across rewrites.
- A verification report alone does not promote status; the metadata
  field must be updated in the same change.
- A change that breaks reproducibility must update the field in the
  same PR.

---

## Recording verification

A verification report is the artifact that earns
`deterministic-confirmed`. The template is in
[VERIFICATION_REPORT_TEMPLATE.md](VERIFICATION_REPORT_TEMPLATE.md).

Reports include:

- Date, commit SHA, fork block, RPC alias, command run.
- `forge test` exit status.
- Output of each required assertion.
- Maintainer or contributor handle.

The verification report is the source of truth. If the report exists
but the metadata says otherwise, the metadata is wrong.

---

## Reproducibility status vs verification status vs RPC capability

These four dimensions are independent and must not be conflated:

| Dimension              | Field                                  | Question it answers                                       |
| ---------------------- | -------------------------------------- | --------------------------------------------------------- |
| Reproducibility status | `reproducibility`                      | Could this PoC, in principle, be reproduced deterministically? |
| Verification status    | `verification_status`                  | Has it actually been run end-to-end against the fork?     |
| RPC capability         | `latest_public_rpc_status`             | What did the most recent public-RPC smoke test produce?   |
| Assertion quality      | `assertion_quality`                    | Are the assertions strong enough to constitute proof?     |

A PoC can simultaneously be:

- `reproducibility: deterministic-likely-but-unverified`
- `verification_status: not-run-no-rpc`
- `latest_public_rpc_status: public-rpc-not-archival`
- `assertion_quality: unknown`

This means: the PoC structure looks sound, no archival RPC has been run, the
public RPC cannot serve historical state, and assertion review is pending.
Each field is independent evidence — none subsume the others.

### Honesty rules for these fields

- **Public RPC failure due to historical state must not downgrade a PoC's
  `reproducibility`.** It is an RPC limitation, not a PoC defect. Record it
  in `latest_public_rpc_status` and move on.
- **A `public-rpc-pass` does not automatically prove research-grade
  verification.** Public-RPC runs sometimes complete without the test
  actually exercising the bug (e.g. weak or missing assertions, wrong fork
  block tolerated by recent state). Promotion to
  `deterministic-confirmed` still requires meaningful assertions and a
  verification report.
- **`verification_status: verified` requires a verification report.** No
  report, no claim.
- **`assertion_quality` is set by human review, not by the runner.** A
  green test bar does not imply strong assertions.

### Quick decision table

| You observed                                            | Record where                          | Do not                                |
| ------------------------------------------------------- | ------------------------------------- | ------------------------------------- |
| Public RPC: `historical state is not available`         | `latest_public_rpc_status: public-rpc-not-archival` | Mark PoC failed.                |
| Public RPC: 429 / rate limit                            | `latest_public_rpc_status: public-rpc-rate-limited` | Mark PoC failed.                |
| Public RPC: timeout / 502 / inconsistent                | `latest_public_rpc_status: public-rpc-unstable`     | Mark PoC failed.                |
| Public RPC: passes, weak assertions                     | `latest_public_rpc_status: public-rpc-pass`         | Auto-promote `reproducibility`. |
| Archival RPC: passes, strong assertions, report written | `verification_status: verified`, `reproducibility: deterministic-confirmed` | Skip the report.                |
| Setup reverts unrelated to RPC                          | investigate; possible PoC issue       | Edit assertions to make it pass.      |
| Exploit reverts mid-flow                                | investigate; possible PoC issue       | Delete the failing leg.               |
| Assertions fail post-exploit                            | investigate; possible bound issue     | Relax bounds without justification.   |
