#!/usr/bin/env python3
"""Create or dry-run Arkheionx remediation issues from an issue plan.

Defensive-by-default behavior:
- dry-run mode makes no network calls;
- create/update modes require a GitHub token and repository;
- deterministic hidden markers prevent duplicate Arkheionx issues;
- generated issues are readiness tasks, not formal audit findings.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


MARKER_PREFIX = "<!-- arkheionx-issue:"
DEFAULT_LABELS = ["arkheionx", "pre-audit-readiness"]
PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "informational": 4,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or dry-run Arkheionx GitHub remediation issues.")
    parser.add_argument("--issue-plan", required=True, help="Arkheionx issue plan JSON path.")
    parser.add_argument("--mode", choices=["dry-run", "create", "update"], default="dry-run")
    parser.add_argument("--github-token", default="", help="GitHub token. Defaults to GITHUB_TOKEN.")
    parser.add_argument("--repo", default="", help="owner/repo. Defaults to GITHUB_REPOSITORY.")
    parser.add_argument("--max-issues", type=int, default=5)
    parser.add_argument("--labels", default="", help="Comma-separated additional labels.")
    parser.add_argument("--assignees", default="", help="Comma-separated assignees.")
    parser.add_argument("--milestone", default="", help="Optional milestone number.")
    parser.add_argument("--grouping", choices=["one-per-finding", "summary"], default="one-per-finding")
    parser.add_argument(
        "--only-priority",
        choices=["critical", "high", "medium", "low", "informational", "all"],
        default="high",
    )
    parser.add_argument("--dry-run-output", default="", help="Optional Markdown dry-run summary path.")
    return parser.parse_args(argv)


def load_issue_plan(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("tool") != "Arkheionx Pre-Audit Scanner":
        raise ValueError("issue plan is not an Arkheionx issue plan")
    return data


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def priority_slug(issue: dict[str, object]) -> str:
    text = str(issue.get("priority", "")).lower()
    for key in PRIORITY_ORDER:
        if key in text:
            return key
    return "informational"


def selected_issues(plan: dict[str, object], grouping: str, only_priority: str, max_issues: int) -> list[dict[str, object]]:
    if grouping == "summary":
        summary = plan.get("summary_issue")
        return [summary] if isinstance(summary, dict) else []
    raw = [item for item in plan.get("issues", []) if isinstance(item, dict)]
    if only_priority != "all":
        threshold = PRIORITY_ORDER[only_priority]
        raw = [item for item in raw if PRIORITY_ORDER.get(priority_slug(item), 99) <= threshold]
    raw.sort(key=lambda item: (PRIORITY_ORDER.get(priority_slug(item), 99), str(item.get("finding_id", ""))))
    return raw[: max(0, max_issues)]


def marker_from_body(body: str) -> str:
    start = body.find(MARKER_PREFIX)
    if start == -1:
        return ""
    end = body.find("-->", start)
    if end == -1:
        return ""
    return body[start : end + 3]


def issue_marker(issue: dict[str, object]) -> str:
    marker = str(issue.get("marker", ""))
    if marker.startswith(MARKER_PREFIX):
        return marker
    return marker_from_body(str(issue.get("body", "")))


def labels_for_issue(issue: dict[str, object], extra_labels: Iterable[str]) -> list[str]:
    labels = set(DEFAULT_LABELS)
    raw = issue.get("labels", [])
    if isinstance(raw, list):
        labels.update(str(item) for item in raw if str(item).strip())
    labels.update(extra_labels)
    return sorted(labels)


def render_dry_run(plan: dict[str, object], issues: list[dict[str, object]]) -> str:
    lines = [
        "# Arkheionx GitHub Issue Dry Run",
        "",
        f"Repository root: `{plan.get('repo_root', '')}`",
        f"Protocol type: `{plan.get('protocol_type', '')}`",
        f"Score: `{plan.get('score', '')}/100`",
        "",
        "No GitHub API calls were made.",
        "",
        "## Issues Selected",
        "",
    ]
    if not issues:
        lines.append("- No issues selected by the current filter.")
    for issue in issues:
        lines.append(f"- `{issue_marker(issue)}` {issue.get('title', '')}")
    lines.extend(
        [
            "",
            "## Safety Note",
            "",
            "These are pre-audit readiness tasks, not formal audit findings and not vulnerability confirmations.",
        ]
    )
    return "\n".join(lines) + "\n"


def github_request(method: str, url: str, token: str, payload: dict[str, object] | None = None) -> object:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "arkheionx-issue-workflow",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def fetch_open_issues(repo: str, token: str) -> list[dict[str, object]]:
    query = urllib.parse.urlencode({"state": "open", "labels": "arkheionx", "per_page": "100"})
    url = f"https://api.github.com/repos/{repo}/issues?{query}"
    data = github_request("GET", url, token)
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def existing_by_marker(open_issues: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for issue in open_issues:
        marker = marker_from_body(str(issue.get("body", "")))
        if marker:
            result[marker] = issue
    return result


def issue_payload(
    issue: dict[str, object],
    extra_labels: list[str],
    assignees: list[str],
    milestone: str,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": str(issue.get("title", "")),
        "body": str(issue.get("body", "")),
        "labels": labels_for_issue(issue, extra_labels),
    }
    if assignees:
        payload["assignees"] = assignees
    if milestone:
        try:
            payload["milestone"] = int(milestone)
        except ValueError:
            pass
    return payload


def run_api_mode(args: argparse.Namespace, plan: dict[str, object], issues: list[dict[str, object]]) -> int:
    token = args.github_token or os.environ.get("GITHUB_TOKEN", "")
    repo = args.repo or os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("Arkheionx issue workflow skipped: create/update requires GitHub token and repository.", file=sys.stderr)
        return 0

    extra_labels = split_csv(args.labels)
    assignees = split_csv(args.assignees)
    try:
        open_issues = fetch_open_issues(repo, token)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"Arkheionx issue workflow warning: could not list existing issues: {exc}", file=sys.stderr)
        return 0

    existing = existing_by_marker(open_issues)
    created = 0
    updated = 0
    skipped = 0
    for issue in issues:
        marker = issue_marker(issue)
        if not marker:
            skipped += 1
            print(f"skip: missing marker for {issue.get('title', '')}")
            continue
        payload = issue_payload(issue, extra_labels, assignees, args.milestone)
        existing_issue = existing.get(marker)
        if existing_issue:
            if args.mode == "update":
                number = existing_issue.get("number")
                url = f"https://api.github.com/repos/{repo}/issues/{number}"
                try:
                    github_request("PATCH", url, token, payload)
                    updated += 1
                    print(f"updated: #{number} {payload['title']}")
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
                    print(f"warning: could not update issue #{number}: {exc}", file=sys.stderr)
            else:
                skipped += 1
                print(f"skip existing: #{existing_issue.get('number')} {payload['title']}")
            continue
        if args.mode == "create":
            url = f"https://api.github.com/repos/{repo}/issues"
            try:
                created_issue = github_request("POST", url, token, payload)
                created += 1
                print(f"created: #{created_issue.get('number', '?')} {payload['title']}" if isinstance(created_issue, dict) else f"created: {payload['title']}")
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
                print(f"warning: could not create issue {payload['title']}: {exc}", file=sys.stderr)
        else:
            skipped += 1
            print(f"skip missing existing issue in update mode: {payload['title']}")
    print(f"Arkheionx issue workflow complete: created={created} updated={updated} skipped={skipped}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        plan = load_issue_plan(Path(args.issue_plan))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: could not read issue plan: {exc}", file=sys.stderr)
        return 1

    issues = selected_issues(plan, args.grouping, args.only_priority, args.max_issues)
    if args.mode == "dry-run":
        output = render_dry_run(plan, issues)
        print(output, end="")
        if args.dry_run_output:
            path = Path(args.dry_run_output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output, encoding="utf-8")
            print(f"Arkheionx issue dry-run written: {path}")
        return 0

    return run_api_mode(args, plan, issues)


if __name__ == "__main__":
    raise SystemExit(main())
