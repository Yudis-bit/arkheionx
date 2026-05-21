# Security

Arkheionx Vault is itself a security-research artifact. The repository should
not introduce security risk to the people who clone it, the protocols it
references, or third parties.

## Reporting issues with this repository

If you find a problem in **this repository's own content** — a PoC that has
been mis-pinned, a metadata error, attribution missing, or, most importantly,
content that may enable attack against a system that isn't actually
patched — please:

1. Do **not** open a public issue with exploitation details.
2. Use the **Documentation issue / unsafe content** template, OR contact the
   maintainer privately via the GitHub profile linked in [BRAND.md](BRAND.md).
3. Include: the file path, the concern, and any references that establish
   patch status (or the lack of it).

## Reporting issues in third-party protocols

This repository does not handle third-party vulnerability reports. If you
have found a vulnerability in a live protocol, **do not open an issue here**.
Contact the protocol directly through their published security channel
(security.txt, Immunefi, HackenProof, audit firm, or direct contact).

## Scope

In scope for security reports against this repo:

- PoCs whose published form might assist attack against an unpatched live
  system.
- Committed credentials, RPC URLs, or other secrets.
- Workflow misconfigurations that leak `${{ secrets.* }}`.
- Supply-chain risks introduced by repository scripts.

Out of scope:

- Vulnerabilities in protocols *referenced* by PoCs. Those go to the protocol.
- Vulnerabilities in third-party tools (Foundry, Anchor, Aptos CLI). Those go
  to the tool maintainers.

## Disclosure handling

If a report concerns content that should be redacted before public discussion:

1. The maintainer acknowledges receipt within a reasonable window.
2. If the concern is valid, the relevant content is moved to embargoed status
   (`status: embargoed` in metadata, code removed, references retained).
3. The reporter is credited if they wish.

There is no bug-bounty program for this repository.

## Secrets policy

- `.env` is gitignored.
- Workflows must not echo `${{ secrets.* }}`.
- Forks must not have access to secrets unless explicitly granted.
- RPC URLs are referenced via env vars in `EVM/foundry.toml`, never inlined.

## Maintainer

Yudistira Putra (`arkheionx`), GitHub
[@Yudis-bit](https://github.com/Yudis-bit).
