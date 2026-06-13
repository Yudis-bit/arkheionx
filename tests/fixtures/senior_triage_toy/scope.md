# Senior Triage Toy — Program Scope

A small synthetic scope used only to exercise the private senior-triage mode.
It is generic and target-agnostic.

## In scope

- `FreshAdapter` value-out path through the newly wired yield source.
- `OldVault` deposit/redeem share accounting.
- Value that can leave the system without caller entitlement.

## Reward / severity

- Valid severity bands: Critical, High, Medium.
- Only Medium and above qualifies for a reward.
- Low and informational issues are not eligible for a reward.
- Maximum bounty applies to High and Critical impact only.

## Out of scope

- Any finding that requires the trusted `owner` or `admin` role is out of scope.
- Centralization risk from the trusted owner/admin is out of scope and invalid.
- Known issues from prior audits are out of scope.
- The first-depositor / inflation behavior on `OldVault.deposit` is a known,
  acknowledged, by-design issue and is out of scope.

## Trusted roles

- The `owner` of OldVault is trusted and assumed to act honestly.
- Findings that rely on the trusted owner acting maliciously are invalid.

## Requirements

- A runnable proof of concept is required for any submission.
