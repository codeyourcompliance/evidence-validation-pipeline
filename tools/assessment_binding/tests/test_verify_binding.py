"""Synthetic assessment-run identity binding tests; no external authority is tested."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools" / "assessment_binding" / "verify_binding.py"
FIX = ROOT / "tools" / "assessment_binding" / "fixtures"
sys.path.insert(0, str(TOOL.parent))
from verify_binding import verify  # noqa: E402

RUN_A = "synthetic-tls-run-001"
RUN_B = "synthetic-tls-run-002"


class AssessmentBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.baseline = self.directory / "baseline.json"
        self.binding = self.directory / "binding.json"
        self.select("a")

    def select(self, which):
        self.baseline.write_bytes((FIX / f"run-{which}-baseline.json").read_bytes())
        self.binding.write_bytes((FIX / f"run-{which}-binding.json").read_bytes())

    def baseline_obj(self):
        return json.loads(self.baseline.read_text(encoding="utf-8"))

    def binding_obj(self):
        return json.loads(self.binding.read_text(encoding="utf-8"))

    def write_json(self, path, obj):
        path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8", newline="\n")

    def check(self, requested=RUN_A):
        return verify(self.baseline, self.binding, requested)

    def test_run_a_binding_consistent(self):
        receipt, exit_code = self.check()
        self.assertEqual((receipt["verification_status"], exit_code), ("binding_consistent", 0))
        self.assertEqual(receipt["baseline_assessment_run_ref"], RUN_A)
        self.assertTrue(receipt["baseline_digest_match"])
        self.assertTrue(receipt["artifact_bindings_match"])

    def test_run_b_binding_consistent_for_b(self):
        self.select("b")
        receipt, exit_code = self.check(RUN_B)
        self.assertEqual((receipt["verification_status"], exit_code), ("binding_consistent", 0))
        self.assertEqual(receipt["binding_assessment_run_ref"], RUN_B)

    def test_valid_b_with_valid_b_binding_rejected_for_a(self):
        self.select("b")
        receipt, exit_code = self.check(RUN_A)
        self.assertEqual((receipt["verification_status"], exit_code), ("requested_run_mismatch", 1))
        self.assertEqual(receipt["reason_codes"], ["requested_run_ref_differs_from_binding"])
        self.assertTrue(receipt["baseline_digest_match"])
        self.assertTrue(receipt["artifact_bindings_match"])

    def test_valid_a_with_valid_a_binding_rejected_for_b(self):
        receipt, exit_code = self.check(RUN_B)
        self.assertEqual((receipt["verification_status"], exit_code), ("requested_run_mismatch", 1))

    def test_valid_b_baseline_with_a_binding_is_not_a(self):
        self.select("b")
        self.binding.write_bytes((FIX / "run-a-binding.json").read_bytes())
        receipt, code = self.check(RUN_A)
        self.assertEqual((receipt["verification_status"], code), ("binding_mismatch", 1))
        self.assertIn("baseline_digest_differs_from_binding", receipt["reason_codes"])
        self.assertIn("baseline_run_ref_differs_from_binding", receipt["reason_codes"])

    def test_valid_a_baseline_with_b_binding_is_not_b(self):
        self.select("a")
        self.binding.write_bytes((FIX / "run-b-binding.json").read_bytes())
        receipt, code = self.check(RUN_B)
        self.assertEqual((receipt["verification_status"], code), ("binding_mismatch", 1))
        self.assertIn("baseline_run_ref_differs_from_binding", receipt["reason_codes"])

    def test_binding_digest_changed_is_mismatch(self):
        record = self.binding_obj()
        record["baseline_sha256"] = "0" * 64
        self.write_json(self.binding, record)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("binding_mismatch", 1))
        self.assertFalse(receipt["baseline_digest_match"])

    def test_binding_role_changed_is_mismatch(self):
        record = self.binding_obj()
        record["artifact_sha256"]["policy"] = "0" * 64
        self.write_json(self.binding, record)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("binding_mismatch", 1))
        self.assertFalse(receipt["artifact_bindings_match"])

    def test_baseline_role_changed_can_not_pass_with_old_anchor(self):
        obj = self.baseline_obj()
        obj["artifact_sha256"]["evaluation_context"] = "0" * 64
        self.write_json(self.baseline, obj)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("binding_mismatch", 1))
        self.assertFalse(receipt["artifact_bindings_match"])

    def test_relabel_b_and_rewrite_binding_can_pass_but_not_authenticate(self):
        self.select("b")
        obj = self.baseline_obj()
        obj["assessment_run_ref"] = RUN_A
        self.write_json(self.baseline, obj)
        anchor = self.binding_obj()
        anchor["assessment_run_ref"] = RUN_A
        anchor["baseline_sha256"] = hashlib.sha256(self.baseline.read_bytes()).hexdigest()
        self.write_json(self.binding, anchor)
        receipt, code = self.check(RUN_A)
        self.assertEqual((receipt["verification_status"], code), ("binding_consistent", 0))
        self.assertEqual(receipt["binding_record_authentication"], "not_assessed")
        self.assertEqual(receipt["binding_record_independence"], "not_assessed")
        self.assertFalse(receipt["historical_replay_verified"])

    def test_baseline_has_only_unattested_identity(self):
        receipt, code = self.check()
        self.assertEqual(code, 0)
        self.assertFalse(receipt["decision_executed"])
        self.assertEqual(receipt["control_status"], "unknown")
        self.assertEqual(receipt["assessment_origin_authentication"], "not_assessed")

    def test_duplicate_key_in_baseline_blocked(self):
        self.baseline.write_text('{"profile":"x","profile":"x"}', encoding="utf-8")
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["baseline_invalid_json"])

    def test_duplicate_key_in_binding_blocked(self):
        self.binding.write_text('{"profile":"x","profile":"x"}', encoding="utf-8")
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["binding_invalid_json"])

    def test_non_json_number_blocked(self):
        self.baseline.write_text('{"invalid":NaN}', encoding="utf-8")
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))

    def test_invalid_run_ref_blocked(self):
        receipt, code = self.check("../../run-x")
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["invalid_requested_assessment_run_ref"])

    def test_missing_baseline_blocked(self):
        self.baseline.unlink()
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["baseline_unavailable"])

    def test_missing_binding_blocked(self):
        self.binding.unlink()
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["binding_unavailable"])

    def test_oversized_baseline_blocked(self):
        self.baseline.write_bytes(b"x" * (1024 * 1024 + 1))
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["baseline_too_large"])

    def test_oversized_binding_blocked(self):
        self.binding.write_bytes(b"x" * (1024 * 1024 + 1))
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["binding_too_large"])

    def test_unsupported_baseline_record_blocked(self):
        obj = self.baseline_obj()
        obj["authority"] = "trusted"
        self.write_json(self.baseline, obj)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["unsupported_synthetic_baseline"])

    def test_unsupported_binding_origin_blocked(self):
        obj = self.binding_obj()
        obj["reference_origin"] = "authenticated"
        self.write_json(self.binding, obj)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))
        self.assertEqual(receipt["reason_codes"], ["unsupported_synthetic_binding"])

    def test_role_is_required(self):
        obj = self.binding_obj()
        del obj["artifact_sha256"]["runtime_requirements"]
        self.write_json(self.binding, obj)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))

    def test_invalid_digest_is_blocked(self):
        obj = self.binding_obj()
        obj["baseline_sha256"] = "not-a-digest"
        self.write_json(self.binding, obj)
        receipt, code = self.check()
        self.assertEqual((receipt["verification_status"], code), ("blocked", 2))

    def test_read_only(self):
        before = (self.baseline.read_bytes(), self.binding.read_bytes())
        receipt, code = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(before, (self.baseline.read_bytes(), self.binding.read_bytes()))
        self.assertFalse(receipt["decision_executed"])

    def test_cli_consistent_and_deterministic(self):
        argv = [sys.executable, str(TOOL), "--baseline", str(self.baseline), "--binding", str(self.binding), "--requested-run-ref", RUN_A]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        first = subprocess.run(argv, capture_output=True, text=True, env=env, check=False)
        second = subprocess.run(argv, capture_output=True, text=True, env=env, check=False)
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout)["verification_status"], "binding_consistent")
        self.assertNotIn(str(self.directory), first.stdout)

    def test_cli_wrong_requested_run_exit_one(self):
        self.select("b")
        run = subprocess.run([sys.executable, str(TOOL), "--baseline", str(self.baseline), "--binding", str(self.binding), "--requested-run-ref", RUN_A], capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)["verification_status"], "requested_run_mismatch")

    def test_cli_bad_reference_exit_two(self):
        run = subprocess.run([sys.executable, str(TOOL), "--baseline", str(self.baseline), "--binding", str(self.directory / "missing"), "--requested-run-ref", RUN_A], capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["verification_status"], "blocked")

    def test_fixtures_distinct_baseline_hashes_both_valid(self):
        a = (FIX / "run-a-baseline.json").read_bytes()
        b = (FIX / "run-b-baseline.json").read_bytes()
        self.assertNotEqual(hashlib.sha256(a).digest(), hashlib.sha256(b).digest())
        self.assertEqual(hashlib.sha256(a).hexdigest(), json.loads((FIX / "run-a-binding.json").read_text())["baseline_sha256"])
        self.assertEqual(hashlib.sha256(b).hexdigest(), json.loads((FIX / "run-b-binding.json").read_text())["baseline_sha256"])
        aobj, bobj = json.loads(a), json.loads(b)
        self.assertNotEqual(aobj["assessment_run_ref"], bobj["assessment_run_ref"])
        self.assertEqual(aobj["recorded"], bobj["recorded"])
        self.assertEqual(aobj["artifact_sha256"], bobj["artifact_sha256"])


if __name__ == "__main__":
    unittest.main()
