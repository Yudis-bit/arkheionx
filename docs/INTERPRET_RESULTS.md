# Interpret Results

ArkheionX output is review context for a human. It is not final truth.

## Mental model

Read every ArkheionX signal as a prompt:

- "look here first";
- "this path moves value";
- "this assumption appears important";
- "this local test area may be weak";
- "this evidence still does not close the question."

Do not read it as:

- "this is vulnerable";
- "this is high severity";
- "this is safe";
- "this is reportable";
- "this will win a bounty."

## Common result types

| result | what it means | what it does not mean |
|---|---|---|
| Review lane | A prioritized human review path. | A finding or severity ranking. |
| Value path | A static map of possible value movement. | A proven execution trace. |
| Role or trust assumption | A dependency the path appears to rely on. | Proof that the dependency is unsafe. |
| Missing or weak test area | Existing local test evidence looks incomplete. | The path is exploitable. |
| Evidence task | A bounded local proof direction. | A completed PoC. |
| Evidence level | How much support local artifacts provide. | Final vulnerability validity. |
| Report-filter classification | Pre-report triage help. | Final acceptance, severity, or disclosure advice. |

## Review priorities

Priority is review order. It is not severity.

A high-priority item usually means the path has value movement, assumptions, weak evidence, complex interaction, or scope relevance. It still requires manual inspection.

## Missing tests

A missing-test signal means ArkheionX did not find convincing local evidence around a path or function. It can be wrong.

Use the signal to ask:

- Is there a meaningful test under a different name?
- Does the test cover the value path, or only touch the function?
- Is the path intentionally untested because it is out of scope?
- What local assertion would close the question?

## Evidence

A passing local test can support a hypothesis. It does not automatically prove exploitability, impact, scope eligibility, or severity.

A failing local test can be useful too. It may kill a weak hypothesis or show that the current proof direction is wrong.

## Case-study discipline

When using ArkheionX in a real review workflow, record:

- the target and review question;
- the value path;
- the trust assumptions;
- the weak or missing test area;
- evidence generated;
- human validation;
- PoC status;
- outcome;
- what ArkheionX did not decide.

See [`CASE_STUDIES.md`](CASE_STUDIES.md).

## Final rule

ArkheionX helps reduce review blindness. It does not replace review.
