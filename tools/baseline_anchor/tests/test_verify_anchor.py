"""Bounded synthetic reference tests; no historical authenticity is asserted."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools" / "baseline_anchor" / "verify_anchor.py"
SELF = ROOT / "tools" / "baseline_anchor" / "fixtures" / "synthetic-self-reference.json"
BASELINE = ROOT / "tools" / "replay_comparison" / "fixtures" / "synthetic-recorded-builtin.json"
sys.path.insert(0, str(TOOL.parent))
from verify_anchor import verify  # noqa: E402


class BaselineAnchorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.baseline = self.path / "baseline.json"
        self.self_ref = self.path / "self-reference.json"
        self.baseline.write_bytes(BASELINE.read_bytes())
        self.self_ref.write_bytes(SELF.read_bytes())
        self.expected = hashlib.sha256(BASELINE.read_bytes()).hexdigest()

    def mutate_baseline(self):
        obj = json.loads(self.baseline.read_text(encoding="utf-8"))
        obj["recorded"]["control_status"] = "fail"
        self.baseline.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        return hashlib.sha256(self.baseline.read_bytes()).hexdigest()

    def rewrite_self_reference(self, digest):
        obj = json.loads(self.self_ref.read_text(encoding="utf-8"))
        obj["baseline_sha256"] = digest
        self.self_ref.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    def test_original_fixture_has_expected_raw_digest(self):
        self.assertEqual(self.expected, "cfec969c3be763a5b977162748116c7461559c0eb2e574faf0c39aebb0c1cb38")

    def test_self_reference_match_is_not_authentication(self):
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual((receipt["verification_status"], code), ("self_consistent", 0))
        self.assertTrue(receipt["digest_match"])
        self.assertFalse(receipt["historical_replay_verified"])
        self.assertEqual(receipt["reference_authentication"], "not_assessed")

    def test_operator_pinned_match_is_not_authentication(self):
        receipt, code = verify(self.baseline, expected_sha256=self.expected)
        self.assertEqual((receipt["verification_status"], code), ("pinned_match", 0))
        self.assertEqual(receipt["reference_mode"], "operator_pinned_digest")
        self.assertEqual(receipt["reference_independence"], "not_assessed")

    def test_self_reference_can_be_rewritten_with_tampered_baseline(self):
        new_digest = self.mutate_baseline()
        self.rewrite_self_reference(new_digest)
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual((receipt["verification_status"], code), ("self_consistent", 0))
        self.assertFalse(receipt["historical_replay_verified"])

    def test_original_pinned_digest_detects_tampered_baseline(self):
        self.mutate_baseline()
        receipt, code = verify(self.baseline, expected_sha256=self.expected)
        self.assertEqual((receipt["verification_status"], code), ("reference_mismatch", 1))
        self.assertEqual(receipt["reason_codes"], ["baseline_digest_differs_from_reference"])

    def test_original_self_reference_detects_tampered_baseline_if_unmodified(self):
        self.mutate_baseline()
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual((receipt["verification_status"], code), ("reference_mismatch", 1))

    def test_replaced_operator_digest_can_also_match_tampering(self):
        new_digest = self.mutate_baseline()
        receipt, code = verify(self.baseline, expected_sha256=new_digest)
        self.assertEqual((receipt["verification_status"], code), ("pinned_match", 0))
        self.assertEqual(receipt["reference_authentication"], "not_assessed")

    def test_invalid_sha256_is_blocked(self):
        receipt, code = verify(self.baseline, expected_sha256="not-a-sha256")
        self.assertEqual((receipt["reason_codes"], code), (["invalid_reference_sha256"], 2))

    def test_uppercase_digest_is_not_accepted_as_canonical(self):
        receipt, code = verify(self.baseline, expected_sha256=self.expected.upper())
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))

    def test_missing_baseline_is_blocked(self):
        receipt, code = verify(self.path / "missing", expected_sha256=self.expected)
        self.assertEqual((receipt["reason_codes"], code), (["baseline_unavailable"], 2))

    def test_missing_self_reference_is_blocked(self):
        receipt, code = verify(self.baseline, self.path / "missing")
        self.assertEqual((receipt["reason_codes"], code), (["self_reference_unavailable"], 2))

    def test_malformed_baseline_is_blocked(self):
        self.baseline.write_text("{invalid", encoding="utf-8")
        receipt, code = verify(self.baseline, expected_sha256=self.expected)
        self.assertEqual((receipt["reason_codes"], code), (["invalid_baseline_json"], 2))

    def test_duplicate_baseline_key_is_blocked(self):
        self.baseline.write_text('{"profile":"tls-replay-v0.1","profile":"tls-replay-v0.1"}', encoding="utf-8")
        receipt, code = verify(self.baseline, expected_sha256=self.expected)
        self.assertEqual((receipt["reason_codes"], code), (["invalid_baseline_json"], 2))

    def test_baseline_profile_mismatch_is_blocked(self):
        obj = json.loads(self.baseline.read_text(encoding="utf-8"))
        obj["profile"] = "different-profile"
        self.baseline.write_text(json.dumps(obj), encoding="utf-8")
        receipt, code = verify(self.baseline, expected_sha256=self.expected)
        self.assertEqual((receipt["reason_codes"], code), (["unsupported_baseline_profile"], 2))

    def test_invalid_self_reference_shape_is_blocked(self):
        self.self_ref.write_text('{"record_type":"unknown"}', encoding="utf-8")
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual((receipt["reason_codes"], code), (["unsupported_self_reference"], 2))

    def test_invalid_self_reference_digest_is_blocked(self):
        self.rewrite_self_reference("not-hex")
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual((receipt["reason_codes"], code), (["invalid_reference_sha256"], 2))

    def test_duplicate_self_reference_key_is_blocked(self):
        self.self_ref.write_text('{"record_type":"x","record_type":"y"}', encoding="utf-8")
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual((receipt["reason_codes"], code), (["invalid_self_reference_json"], 2))

    def test_oversized_baseline_is_blocked(self):
        self.baseline.write_bytes(b"x" * (1024 * 1024 + 1))
        receipt, code = verify(self.baseline, expected_sha256=self.expected)
        self.assertEqual((receipt["reason_codes"], code), (["baseline_too_large"], 2))

    def test_no_evidence_modification_and_no_decision(self):
        before = (self.baseline.read_bytes(), self.self_ref.read_bytes())
        receipt, code = verify(self.baseline, self.self_ref)
        self.assertEqual(code, 0)
        self.assertEqual(before, (self.baseline.read_bytes(), self.self_ref.read_bytes()))
        self.assertFalse(receipt["decision_executed"])
        self.assertEqual(receipt["control_status"], "unknown")

    def test_cli_is_deterministic_and_has_no_host_paths(self):
        argv = [sys.executable, str(TOOL), "--baseline", str(self.baseline), "--expected-sha256", self.expected]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        run1 = subprocess.run(argv, text=True, capture_output=True, env=env, check=False)
        run2 = subprocess.run(argv, text=True, capture_output=True, env=env, check=False)
        self.assertEqual(run1.returncode, 0)
        self.assertEqual(run1.stdout, run2.stdout)
        self.assertNotIn(str(self.path), run1.stdout)
        self.assertEqual(json.loads(run1.stdout)["verification_status"], "pinned_match")

    def test_cli_mismatch_exit_one(self):
        self.mutate_baseline()
        run = subprocess.run([sys.executable, str(TOOL), "--baseline", str(self.baseline), "--expected-sha256", self.expected], text=True, capture_output=True, check=False)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)["verification_status"], "reference_mismatch")

    def test_cli_blocked_exit_two(self):
        run = subprocess.run([sys.executable, str(TOOL), "--baseline", str(self.path / "missing"), "--expected-sha256", self.expected], text=True, capture_output=True, check=False)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["verification_status"], "blocked")

    def test_no_reference_or_two_references_is_blocked_in_api(self):
        self.assertEqual(verify(self.baseline)[1], 2)
        self.assertEqual(verify(self.baseline, self.self_ref, self.expected)[1], 2)


if __name__ == "__main__":
    unittest.main()
