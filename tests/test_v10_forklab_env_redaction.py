"""V10 fork lab: secret redaction."""
import unittest

from arkheionx.forklab import secret_redaction


class EnvRedactionTest(unittest.TestCase):
    def test_rpc_url_is_redacted(self):
        text = "rpc = https://eth-mainnet.alchemyapi.io/v2/SuperSecretKey123"
        out = secret_redaction.redact(text)
        self.assertNotIn("https://", out)
        self.assertNotIn("SuperSecretKey123", out)
        self.assertIn("REDACTED", out)

    def test_ws_url_is_redacted(self):
        out = secret_redaction.redact("ws = wss://node.example.com/abc")
        self.assertNotIn("wss://", out)

    def test_private_key_is_redacted(self):
        key = "0x" + "a" * 64
        out = secret_redaction.redact(f"pk = {key}")
        self.assertNotIn(key, out)
        self.assertIn("[REDACTED_KEY]", out)

    def test_scan_reports_warnings(self):
        warnings = secret_redaction.scan("see https://rpc.example/secret")
        self.assertTrue(warnings)

    def test_clean_text_untouched(self):
        clean = "Use the FORK_RPC_URL env var (name only)."
        self.assertEqual(secret_redaction.redact(clean), clean)
        self.assertEqual(secret_redaction.scan(clean), [])


if __name__ == "__main__":
    unittest.main()
