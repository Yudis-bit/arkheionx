# GitHub Surface Inventory

## Issue templates

| template | category | status | notes |
|---|---|---|---|
| `.github/ISSUE_TEMPLATE/feedback.md` | core public feedback | keep | General product feedback with safety boundary. |
| `.github/ISSUE_TEMPLATE/documentation_issue.md` | docs | keep | Covers docs corrections and unsafe content concerns. |
| `.github/ISSUE_TEMPLATE/bug_report.md` | historical fixture / reproducibility | keep | Reframed as broken validation fixture while preserving the filename. |
| `.github/ISSUE_TEMPLATE/poc_verification_issue.md` | historical fixture / reproducibility | keep | Reframed as validation fixture reproducibility while preserving the filename. |
| `.github/ISSUE_TEMPLATE/assertion_hardening.md` | research candidate / fixture hardening | keep | Useful for strengthening historical validation fixtures. |
| `.github/ISSUE_TEMPLATE/research_candidate.md` | research candidate | keep | Useful for proposing historical incident fixtures; avoid live-target framing. |
| `.github/ISSUE_TEMPLATE/unsafe_content_report.md` | safety | keep | Important public safety escape hatch. |
| `.github/ISSUE_TEMPLATE/false_negative.yml` | false negative calibration | keep | Useful calibration path. |
| `.github/ISSUE_TEMPLATE/false_positive.yml` | false positive calibration | keep | Useful calibration path. |
| `.github/ISSUE_TEMPLATE/false_positive_calibration.yml` | duplicate/calibration | needs review | Overlaps with `false_positive.yml` and `false_positive_report.yml`. |
| `.github/ISSUE_TEMPLATE/false_positive_report.yml` | duplicate/calibration | needs review | Overlaps with `false_positive.yml` and calibration template. |
| `.github/ISSUE_TEMPLATE/demo_output_noise.md` | output calibration | keep | Useful for review-map quality feedback. |
| `.github/ISSUE_TEMPLATE/report_quality_feedback.yml` | output calibration | keep | Useful for report wording/actionability. |
| `.github/ISSUE_TEMPLATE/rule_calibration_request.yml` | rule pack | keep | Useful for tuning signals. |
| `.github/ISSUE_TEMPLATE/rule_request.yml` | rule pack | keep | Useful for new defensive signal requests. |
| `.github/ISSUE_TEMPLATE/external_evaluation_feedback.yml` | external validation | needs review | Overlaps with `external_validation_feedback.yml`. |
| `.github/ISSUE_TEMPLATE/external_validation_feedback.yml` | external validation | keep | Better aligned with Phase 1 external validation language. |
| `.github/ISSUE_TEMPLATE/github_action_feedback.yml` | GitHub Action | keep | Useful while action docs remain supported. |
| `.github/ISSUE_TEMPLATE/pre_audit_readiness_request.yml` | launch/business | keep but de-emphasize | Commercial/request surface; not core technical feedback. |
| `.github/ISSUE_TEMPLATE/pre_audit_sprint_request.yml` | launch/business | keep but de-emphasize | Commercial/request surface; not core technical feedback. |
| `.github/ISSUE_TEMPLATE/launch_report_request.yml` | launch/business | needs review | May feel sales-first for a public security tooling repo. |
| `.github/ISSUE_TEMPLATE/config.yml` | issue picker config | update later | Contact links still point to old repo slug until rename decision. |

## Cleanup recommendation

Do not delete templates in Phase 2. First decide the GitHub repo rename and then consolidate:

- merge the three false-positive templates into one;
- merge external evaluation and external validation into one;
- consider hiding launch/business templates from the default issue picker if public technical feedback is the priority;
- update `config.yml` contact links only when the old repository slug redirects reliably.
