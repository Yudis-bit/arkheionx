#!/usr/bin/env python3
"""Post or update the Arkheionx pull request comment.

This script is intentionally small and opt-in:
- it only runs when a workflow provides a GitHub token;
- it only reads a local comment body and the GitHub event payload;
- it updates an existing Arkheionx marker comment in update mode;
- it exits successfully when context or permissions are missing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


MARKER = "<!-- arkheionx-pre-audit-comment -->"
API_ROOT = "https://api.github.com"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_pr_number(event: dict) -> int | None:
    pull_request = event.get("pull_request")
    if isinstance(pull_request, dict) and pull_request.get("number"):
        return int(pull_request["number"])
    if event.get("number") and event.get("issue", {}).get("pull_request"):
        return int(event["number"])
    return None


def find_marker_comment(comments: list[dict], marker: str = MARKER) -> dict | None:
    for comment in comments:
        body = str(comment.get("body", ""))
        if marker in body:
            return comment
    return None


def github_request(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, object]:
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "arkheionx-pre-audit-action",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
        return response.status, json.loads(payload) if payload else {}


def post_or_update_comment(comment_file: Path, mode: str) -> int:
    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")

    if not token:
        print("Arkheionx PR comment skipped: GITHUB_TOKEN is not set.")
        return 0
    if not repository:
        print("Arkheionx PR comment skipped: GITHUB_REPOSITORY is not set.")
        return 0
    if not event_path or not Path(event_path).exists():
        print("Arkheionx PR comment skipped: GITHUB_EVENT_PATH is missing.")
        return 0
    if not comment_file.exists():
        print(f"Arkheionx PR comment skipped: comment file not found: {comment_file}")
        return 0

    event = load_json(Path(event_path))
    pr_number = extract_pr_number(event)
    if pr_number is None:
        print("Arkheionx PR comment skipped: not a pull_request event.")
        return 0

    body = comment_file.read_text(encoding="utf-8")
    if MARKER not in body:
        body = MARKER + "\n\n" + body

    comments_url = f"{API_ROOT}/repos/{repository}/issues/{pr_number}/comments"
    try:
        _, comments = github_request("GET", comments_url + "?per_page=100", token)
        if not isinstance(comments, list):
            print("Arkheionx PR comment warning: unexpected comments response; creating a new comment.")
            comments = []
        existing = find_marker_comment(comments)
        if existing and mode == "update":
            comment_id = existing.get("id")
            if not comment_id:
                print("Arkheionx PR comment warning: marker comment had no id; creating a new comment.")
            else:
                update_url = f"{API_ROOT}/repos/{repository}/issues/comments/{comment_id}"
                github_request("PATCH", update_url, token, {"body": body})
                print("Arkheionx PR comment updated.")
                return 0
        github_request("POST", comments_url, token, {"body": body})
        print("Arkheionx PR comment created.")
        return 0
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        print(f"Arkheionx PR comment warning: GitHub API returned {exc.code}: {detail[:500]}")
        return 0
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Arkheionx PR comment warning: {exc}")
        return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post or update an Arkheionx pull request comment.")
    parser.add_argument("--comment-file", required=True, help="Markdown file containing the PR comment body.")
    parser.add_argument("--mode", choices=["update", "append"], default="update", help="Update marker comment or append a new comment.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return post_or_update_comment(Path(args.comment_file), args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
