# What ArkheionX is not

ArkheionX is a local, static review-map tool for DeFi smart-contract
repositories. To keep expectations honest, here is what it explicitly does
**not** do.

ArkheionX is **not**:

- **not an audit**, and not a replacement for one. It is a pre-review readiness
  aid; a formal audit is still recommended.
- **not a vulnerability guarantee.** It does not confirm vulnerabilities and
  does not prove their absence.
- **not an exploit tool.** It does not generate, simulate, or run exploits or
  attacks, and it produces no attack payloads.
- **not a severity oracle.** It does not assign final severity, impact, or
  exploitability.
- **not a live-chain or RPC scanner.** It does not call RPC endpoints, fork
  networks, broadcast transactions, or read deployed contracts.
- **not a secrets handler.** It does not request or accept private keys, seed
  phrases, mnemonics, or production credentials.
- **not a replacement for manual review.** A human makes every security
  decision; ArkheionX only organizes context.
- **not a replacement for tests, fuzzing, or formal verification.** It points at
  gaps; you still write, run, and judge the tests.
- **not a proof of safety.** A clean review map does not mean a protocol is
  safe, and a passing local test does not prove the absence of a bug.
- **not a source of adoption or production claims.** ArkheionX makes no claim of
  users, customers, or production usage.

## Why this matters

Security tooling earns trust by being precise about its limits. ArkheionX is
designed to help builders and reviewers reason about value flow, assumptions,
and missing tests *before* an audit — not to stand in for one. If you need a
verdict on whether code is safe, that decision belongs to a human reviewer and,
where appropriate, a formal audit.

See also: [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md),
[`SECURITY.md`](SECURITY.md), and [`ETHICS.md`](ETHICS.md).
