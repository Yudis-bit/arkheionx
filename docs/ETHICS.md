# Ethics

Arkheionx is defensive security research and pre-audit readiness tooling. The
principles below are non-negotiable.

## Scope

- Defensive only. Material in this repository exists to help engineers,
  auditors, researchers, and indie builders prevent repeated failures.
- Historical and patched preferred. PoCs target incidents that have already
  occurred and protocols that have already been remediated, abandoned, or
  forked away from the vulnerable state.
- Authorized code only. The pre-audit scanner is for repositories you own or
  are explicitly authorized to review.
- No live targeting. Nothing here is intended to be run against unpatched
  production systems without authorization.

## Scanner Boundaries

The Arkheionx pre-audit scanner:

- inspects local repository files only;
- does not call live chains;
- does not require RPC by default;
- does not submit transactions;
- does not test deployed contracts;
- does not adapt historical PoCs to live targets;
- does not collect secrets;
- does not create remote issues by default.

The scanner may:

- detect static risk signals;
- identify missing tests;
- map design patterns to historical exploit classes;
- generate Markdown and JSON reports;
- generate SARIF, baseline, diff, checklist, and issue-plan artifacts;
- generate safe Foundry invariant skeletons;
- recommend defensive review;
- recommend formal audit.

Optional GitHub issue creation is separate, explicit, token-based, capped by
`--max-issues`, and intended only for repositories you own or are authorized to
manage. Dry-run mode makes no GitHub API calls.

## Use

By reading or using anything in this repository, you accept that:

1. You will not adapt these PoCs or readiness rules to attack systems without
   explicit written authorization from the system owner.
2. You will not use these materials to extract value, data, access, or control
   from any party without consent.
3. You will obey all applicable laws, contracts, program rules, and disclosure
   obligations in your jurisdiction.
4. You will not put private keys, mnemonics, RPC credentials, or confidential
   production details into public issues or reports.

These rules apply regardless of how educational a request sounds.

## Report Language

Arkheionx uses:

- risk signal;
- readiness gap;
- review recommended;
- historical pattern similarity;
- missing invariant;
- audit blocker;
- defensive check.

Arkheionx avoids:

- static-scan language that claims proof;
- safety guarantee language;
- bounty outcome promises;
- claim that a protocol can be drained;
- active attack instructions.

## Disclosure

If a PoC or readiness rule appears relevant to an unpatched live system, do not
test it against that system. Instead:

1. Contact the protocol through its published security channel.
2. Follow coordinated disclosure or program rules.
3. Wait for fix and disclosure window.
4. Add public educational material only after the issue is resolved and safe to
   discuss.

## Embargoed Work

If work is under disclosure embargo, exploit details are not published here
until the embargo lifts. The `metadata/registry.json` `status` field of
`embargoed` exists for this purpose; embargoed entries do not include exploit
code.

## Reporting Unsafe Content

If you believe something in this repository:

- enables attack against an unpatched live system;
- contains private credentials or non-public protocol material;
- violates these principles;

open an unsafe content issue or contact the maintainer through the GitHub
profile listed in [`SECURITY.md`](SECURITY.md).

## Affiliation

This repository is independent. It is not endorsed by, partnered with, or
affiliated with any audit firm, contest platform, bounty program, protocol, or
ecosystem unless such a relationship is explicitly documented in committed
public artifacts.
