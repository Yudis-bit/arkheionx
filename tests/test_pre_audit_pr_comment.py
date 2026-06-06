import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import post_pr_comment


class PreAuditPrCommentTests(unittest.TestCase):
    def test_extract_pr_number_from_pull_request_event(self) -> None:
        self.assertEqual(post_pr_comment.extract_pr_number({"pull_request": {"number": 42}}), 42)
        self.assertIsNone(post_pr_comment.extract_pr_number({"workflow_dispatch": {}}))

    def test_find_marker_comment(self) -> None:
        comments = [
            {"id": 1, "body": "normal comment"},
            {"id": 2, "body": f"{post_pr_comment.MARKER}\n\nArkheionx"},
        ]
        self.assertEqual(post_pr_comment.find_marker_comment(comments)["id"], 2)

    def test_missing_token_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            comment_file = Path(tmp) / "comment.md"
            comment_file.write_text(post_pr_comment.MARKER + "\nbody\n", encoding="utf-8")
            with mock.patch.dict("os.environ", {}, clear=True):
                self.assertEqual(post_pr_comment.post_or_update_comment(comment_file, "update"), 0)


if __name__ == "__main__":
    unittest.main()
