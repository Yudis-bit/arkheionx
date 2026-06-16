"""Tests for the hunter Address Parser v2 (all formats + strict error statuses)."""
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.addresses import is_address, parse_addresses

A1 = "0x1111111111111111111111111111111111111111"
A2 = "0x2222222222222222222222222222222222222222"
A3 = "0x3333333333333333333333333333333333333333"


def write_tmp(data, *, raw=None):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    tmp.write(raw if raw is not None else json.dumps(data))
    tmp.close()
    return tmp.name


class AddressValidatorTests(unittest.TestCase):
    def test_is_address(self) -> None:
        self.assertTrue(is_address(A1))
        self.assertFalse(is_address("0x123"))
        self.assertFalse(is_address("not-an-address"))
        self.assertFalse(is_address(A1[:-1] + "g"))


class AddressFormatTests(unittest.TestCase):
    def test_flat_map(self) -> None:
        r = parse_addresses(write_tmp({"Vault": A1, "Pool": A2}))
        self.assertEqual(r.status, M.ADDRESS_OK)
        self.assertEqual(r.detected_format, "flat_map")
        self.assertEqual({a["name"] for a in r.addresses}, {"Vault", "Pool"})

    def test_contracts_array(self) -> None:
        r = parse_addresses(write_tmp({"contracts": [
            {"name": "Vault", "address": A1, "category": "core", "expected_implementation": A3}]}))
        self.assertEqual(r.status, M.ADDRESS_OK)
        self.assertEqual(r.detected_format, "contracts_array")
        self.assertEqual(r.addresses[0]["expected_implementation"], A3.lower())

    def test_program_chain_contracts(self) -> None:
        r = parse_addresses(write_tmp({"program": "P", "chain": "ethereum", "contracts": [
            {"name": "Pool", "address": A2, "proxy_expected": True, "expected_implementation": A3}]}))
        self.assertEqual(r.status, M.ADDRESS_OK)
        self.assertEqual(r.detected_format, "program_contracts")
        self.assertTrue(r.addresses[0]["proxy_expected"])

    def test_environment_map(self) -> None:
        r = parse_addresses(write_tmp({"mainnet": {"Vault": A1}, "testnet": {"Vault": A2}}))
        self.assertEqual(r.status, M.ADDRESS_OK)
        self.assertEqual(r.detected_format, "environment_map")
        self.assertIn("mainnet", r.networks)
        self.assertIn("testnet", r.networks)

    def test_chains_map_nested(self) -> None:
        r = parse_addresses(write_tmp({"chains": {
            "1": {"contracts": [{"name": "Vault", "address": A1}]},
            "8453": {"contracts": [{"name": "BaseVault", "address": A2}]}}}))
        self.assertEqual(r.status, M.ADDRESS_OK)
        self.assertEqual(r.detected_format, "chains_map")
        self.assertEqual(set(r.chain_ids), {"1", "8453"})

    def test_list_of_objects(self) -> None:
        r = parse_addresses(write_tmp([{"name": "Vault", "address": A1}]))
        self.assertEqual(r.status, M.ADDRESS_OK)
        self.assertEqual(r.detected_format, "list_of_objects")

    def test_normalization_lowercases(self) -> None:
        r = parse_addresses(write_tmp({"Vault": A1.upper().replace("0X", "0x")}))
        self.assertEqual(r.addresses[0]["address"], A1.lower())


class AddressErrorTests(unittest.TestCase):
    def test_invalid_address_non_empty_is_parse_error(self) -> None:
        r = parse_addresses(write_tmp({"Vault": "0xnotvalid"}))
        self.assertEqual(r.status, M.ADDRESS_PARSE_ERROR)
        self.assertTrue(r.errors)
        self.assertTrue(r.path)

    def test_non_empty_but_zero_parsed_is_parse_error(self) -> None:
        r = parse_addresses(write_tmp({"meta": "no addresses here"}))
        self.assertEqual(r.status, M.ADDRESS_PARSE_ERROR)

    def test_empty_file(self) -> None:
        r = parse_addresses(write_tmp(None, raw=""))
        self.assertEqual(r.status, M.ADDRESS_FILE_EMPTY)

    def test_missing_file(self) -> None:
        r = parse_addresses("/path/does/not/exist.json")
        self.assertEqual(r.status, M.ADDRESS_FILE_MISSING)

    def test_none_provided(self) -> None:
        r = parse_addresses("")
        self.assertEqual(r.status, M.ADDRESS_NONE_PROVIDED)

    def test_explicit_empty_contracts_is_valid(self) -> None:
        r = parse_addresses(write_tmp({"contracts": []}))
        self.assertEqual(r.status, M.ADDRESS_EMPTY_CONTRACTS)
        self.assertEqual(r.addresses, [])

    def test_invalid_json_non_empty_is_parse_error(self) -> None:
        r = parse_addresses(write_tmp(None, raw="{not json"))
        self.assertEqual(r.status, M.ADDRESS_PARSE_ERROR)


if __name__ == "__main__":
    unittest.main()
