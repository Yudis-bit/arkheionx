# Ethics

Arkheionx Vault is a defensive security research archive. The principles below
are non-negotiable.

## Scope

- **Defensive only.** Material in this repository exists to help engineers,
  auditors, and researchers understand failure modes well enough to prevent
  them.
- **Historical and patched preferred.** PoCs target incidents that have already
  occurred and protocols that have already been remediated, abandoned, or
  forked away from the vulnerable state.
- **No live targeting.** Nothing in this repository is intended to be run
  against unpatched production systems the maintainer is not authorized to
  test.

## Use

By reading or using anything in this repository, you accept that:

1. You will not adapt these PoCs to attack systems without explicit, written
   authorization from the system's owner.
2. You will not use these materials to extract value (funds, data, access)
   from any party without their consent.
3. You will obey all applicable laws, contracts, and disclosure obligations
   in your jurisdiction.

These rules apply regardless of how "educational" your reframing sounds.

## Disclosure

If a PoC in this repository describes a vulnerability you believe is **not yet
patched** in a live system, do not run it against that system. Instead:

1. Contact the protocol's security team through their published channel
   (security.txt, Immunefi, HackenProof, direct contact).
2. Wait for confirmation, fix, and disclosure window.
3. Once the issue is resolved, the PoC may be added here as historical record.

## Embargoed work

If the maintainer is currently working under disclosure embargo (Immunefi,
HackenProof, contest, private engagement, direct disclosure), no exploit
details are published in this repository until the embargo lifts. The
`metadata/registry.json` `status` field of `embargoed` exists for this
purpose; embargoed entries do not include exploit code.

## Reporting unsafe content

If you believe something in this repository:

- enables attack against an unpatched live system,
- contains private credentials or non-public protocol material, or
- otherwise violates these principles,

open an issue using the **Documentation issue / unsafe content** template, or
contact the maintainer at the GitHub profile listed in [SECURITY.md](SECURITY.md).

## Affiliation

This repository is independent. It is not endorsed by, partnered with, or
affiliated with any audit firm, contest platform, or bounty program. References
to such organizations are for attribution to public post-mortems only.
