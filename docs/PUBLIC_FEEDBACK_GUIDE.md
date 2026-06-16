# Public Feedback Guide

ArkheionX needs clear technical feedback from people who understand smart contract review.

Good feedback is specific. It says what output helped, what was wrong, what was noisy, and what would be needed before real usage.

## Safe testing rule

Use ArkheionX only on repositories you own or are authorized to review.

Do not share:

- private keys;
- mnemonics;
- RPC credentials;
- production secrets;
- private repository contents without permission;
- unpatched vulnerability details;
- exploit steps for live targets.

## Feedback that helps most

- A value path ArkheionX mapped correctly.
- A role or trust assumption it missed.
- A missing-test signal that was useful.
- A missing-test signal that was noise.
- An evidence task that was testable.
- An evidence task that was vague or unsafe.
- A term that would confuse auditors or protocol engineers.
- A case-study format that would make the project more credible.

## Questions for reviewers

- Does the review map match how you reason through a protocol?
- Which outputs are useful?
- Which outputs are noise?
- What would you need before using this in a real audit?
- Which terminology feels wrong?
- What would make this safer?
- Which case study would make this credible?

## Questions for protocol teams

- Did the output identify assets and value paths that matter?
- Did it capture privileged roles accurately?
- Did it surface useful missing-test areas?
- Did it miss protocol-specific assumptions?
- Was any output too generic to act on?
- Would you run this before an audit if it were easier to install or interpret?

## How to send feedback

Use the repository issue tracker for public, non-sensitive feedback.

Use private channels for:

- unpublished security issues;
- private repository details;
- confidential protocol context;
- case studies that need permission before publication.

## What feedback does not mean

Feedback does not create an audit relationship, security certification, endorsement, bounty guarantee, or acceptance claim.

ArkheionX remains review infrastructure. Human review remains required.
