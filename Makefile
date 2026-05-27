.PHONY: demo test validate search

demo:
	python3 scripts/pre_audit_scan.py \
		--root examples/oracle-staking-fixture \
		--protocol-type auto \
		--output examples/reports/demo-pre-audit-report.md \
		--json-output examples/reports/demo-report.json \
		--sarif-output examples/reports/demo.sarif.json \
		--baseline-output examples/reports/demo.baseline.json \
		--issue-plan-output examples/reports/demo-issue-plan.json \
		--issue-checklist-output examples/reports/demo-issue-checklist.md \
		--launch-report-output examples/reports/demo-launch-report.md \
		--sprint-plan-output examples/reports/demo-sprint-plan.md \
		--sprint-days 5 \
		--contest-readiness-output examples/reports/demo-contest-readiness.md \
		--executive-summary-output examples/reports/demo-executive-summary.md \
		--remediation-roadmap-output examples/reports/demo-remediation-roadmap.md

test:
	python3 -m unittest discover -s tests -p "test_*.py"

validate:
	python3 -m py_compile \
		scripts/pre_audit_scan.py \
		scripts/generate_search_index.py \
		scripts/post_pr_comment.py \
		scripts/create_github_issues.py \
		scripts/generate_knowledge_graph.py \
		scripts/generate_feedback_dashboard.py \
		scripts/generate_paid_offer_index.py \
		scripts/generate_ecosystem_report.py \
		scripts/generate_test_plan.py \
		scripts/validate_config.py \
		scripts/search_knowledge.py \
		scripts/check_docs_links.py \
		scripts/check_version_consistency.py \
		scripts/check_safety_wording.py \
		arkheionx/__init__.py \
		arkheionx/version.py \
		arkheionx/core/models.py \
		arkheionx/core/paths.py \
		arkheionx/core/files.py \
		arkheionx/core/constants.py \
		arkheionx/core/safety.py \
		arkheionx/config/loader.py \
		arkheionx/config/schema.py \
		arkheionx/config/suppressions.py \
		arkheionx/rules/registry.py \
		arkheionx/rules/ids.py \
		arkheionx/reports/artifacts.py \
		arkheionx/reports/profiles.py \
		arkheionx/reports/summary.py \
		arkheionx/reports/ux.py \
		arkheionx/knowledge/search.py \
		arkheionx/generators/test_plan.py \
		arkheionx/generators/feedback_dashboard.py \
		arkheionx/generators/paid_offer_index.py \
		arkheionx/generators/ecosystem_report.py \
		arkheionx/cli/main.py
	python3 -m arkheionx.cli.main version
	python3 -m arkheionx.cli.main doctor
	python3 scripts/validate_config.py --config examples/arkheionx.config.example.json
	python3 scripts/validate_config.py --config examples/configs/minimal.config.json
	python3 scripts/validate_config.py --config examples/configs/ci.config.json
	python3 scripts/validate_config.py --config examples/configs/amm-lending.config.json
	python3 scripts/validate_config.py --config examples/configs/strict-audit-prep.config.json
	python3 scripts/validate_config.py --config examples/configs/suppressions.config.json
	python3 -m unittest discover -s tests -p "test_*.py"
	python3 scripts/generate_knowledge_graph.py --check
	python3 scripts/generate_feedback_dashboard.py --check
	python3 scripts/generate_paid_offer_index.py --check
	python3 scripts/generate_ecosystem_report.py --check
	python3 scripts/generate_test_plan.py --check
	python3 scripts/search_knowledge.py "oracle stale price"
	python3 scripts/generate_search_index.py --check
	python3 scripts/check_docs_links.py --check
	python3 scripts/check_version_consistency.py --check
	python3 scripts/check_safety_wording.py --strict

search:
	python3 scripts/search_knowledge.py "oracle stale price"
