# Noise Reduction

Arkheionx report UX focuses on making static readiness signals easier to review
without hiding findings silently.

v1.8.0 improves noise handling by:

- grouping findings by rule family and confidence;
- keeping low-confidence findings visible but easier to separate;
- carrying confidence reasons into reports and issue plans;
- limiting evidence volume by output profile;
- surfacing suppressions and suppression review reminders;
- retaining generated artifact ignore summaries;
- using readiness wording instead of vulnerability-confirmation wording.

For weak or keyword-heavy signals, reports prefer language such as
`manual review recommended` and point toward precise defensive tests.

Suppressions should be scoped, documented, and reviewed before launch or
external review. They are not deleted from the report; they are summarized
separately.
