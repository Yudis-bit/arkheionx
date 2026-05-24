# Content Playbook

Content should make the archive legible to the people who might sponsor it,
hire for scoped work, or invite a workshop.

The tone stays technical and calm. Every post should teach one concrete thing.

## Content Pillars

1. **Assertion quality.** Logs are not proof; hard assertions are.
2. **Root cause.** Name the broken assumption, not only the bug class.
3. **Invariant thinking.** Say what should have remained true.
4. **Verification honesty.** Public RPC smoke is not archival verification.
5. **Auditor prompts.** Convert incidents into review questions.

## 30-Day Calendar

| Day | Topic | CTA |
|---:|---|---|
| 1 | Why `console.log(attackerBalance)` is not proof | Link to assertion standard |
| 2 | Parity Multisig: initializer as attack surface | Link to registry entry |
| 3 | BEC overflow: supply invariant break | Offer workshop |
| 4 | What `assertion_quality: weak` means | Link to quality matrix |
| 5 | Public RPC vs archival RPC | Link to fork verification docs |
| 6 | How to write an attacker profit assertion | Link to commercial page |
| 7 | Weekly archive progress note | Ask for sponsorship |
| 8 | bZx iETH: accounting mismatch fingerprint | Link to PoC |
| 9 | Why exact profit assertions can be brittle | Link to assertion hygiene |
| 10 | DODO: initialization bug checklist | Offer training |
| 11 | What a verification report should contain | Link to template |
| 12 | How to classify an exploit category | Link to taxonomy |
| 13 | Turning a post-mortem into a PoC checklist | Offer report work |
| 14 | Weekly weak-entry hardening queue | Ask for sponsor |
| 15 | Harvest: spot price as trust boundary | Offer workshop |
| 16 | What belongs in setup vs exploit body | Link to PoC standard |
| 17 | Why L4 is harder than a green test | Link to maturity model |
| 18 | How victim loss assertions differ by category | Link to assertion standard |
| 19 | Building auditor prompts from incidents | Link to auditor checklist |
| 20 | What sponsorship funds this month | Link to sponsorship page |
| 21 | Weekly archive progress note | Ask for sponsorship |
| 22 | Pickle/Cheese Bank: arbitrary-call lesson | Offer hardening sprint |
| 23 | yETH: invariant manipulation as case-study candidate | Link to registry |
| 24 | Why weak PoCs are still useful but not proof | Link to quality matrix |
| 25 | How to avoid inflated verification claims | Link to reproducibility standard |
| 26 | What a paid assertion hardening sprint includes | Link to services |
| 27 | Workshop module preview: assertion families | Offer training |
| 28 | Weekly hardening queue | Ask for sponsor |
| 29 | One invariant every DeFi reviewer should write down | Link to checklist |
| 30 | Month-end archive metrics | Ask for scoped inquiries |

## Post Templates

### Assertion Lesson

```text
Exploit replay lesson:

A passing test is not proof unless the post-state is asserted.

For <incident>, the important check is not "the call succeeded".
It is:

- attacker balance changed by X
- victim balance / control state changed by Y
- invariant Z no longer holds

This is why Arkheionx Vault tracks assertion quality separately from runtime
verification.
```

### Case Study Hook

```text
Historical DeFi exploit anatomy:

Incident: <name>
Root cause: <broken assumption>
Broken invariant: <what should have held>
Assertion family: <F1/F2/F3/etc.>

The useful lesson for auditors is not the exploit recipe. It is the protocol
assumption that made the recipe possible.
```

### Sponsorship Ask

```text
Arkheionx Vault has <N> historical PoCs.

Current bottleneck:
- <X> weak assertions remaining
- <Y> archival verified entries
- <Z> public-RPC smoke attempts

Sponsorship funds the slow work: assertion hardening, verification reports, and
case-study writing.
```

### Service CTA

```text
If your internal exploit PoC ends with logs but no hard assertions, I can help
turn it into a reviewer-readable proof:

- assertion patch
- invariant map
- root-cause notes
- verification checklist

Historical, patched, or authorized targets only.
```

## Rules

- One concept per post.
- Mention exact dates, blocks, categories, or assertion families when useful.
- Never imply live-target capability.
- Never claim verification that the maturity index does not support.
- Link back to generated reports, not manual claims.
