from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from replay import replay


ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads((ROOT / "input/evidence.json").read_text(encoding="utf-8"))
        self.context = json.loads((ROOT / "input/evaluation-context.json").read_text(encoding="utf-8"))
        self.policy = ROOT / "policy/tls_certificate.rego"

    def run_case(self, evidence: dict, context: dict, mutate_after_hash=None):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            evidence_path = tmpdir / "evidence.json"
            context_path = tmpdir / "context.json"
            digest_path = tmpdir / "evidence.sha256"
            write_json(evidence_path, evidence)
            digest_path.write_text(digest(evidence_path) + "\n", encoding="utf-8")
            if mutate_after_hash is not None:
                mutated = json.loads(evidence_path.read_text(encoding="utf-8"))
                mutate_after_hash(mutated)
                write_json(evidence_path, mutated)
            write_json(context_path, context)
            return replay(evidence_path, digest_path, context_path, self.policy, "builtin", "opa")

    def test_valid_safe_certificate_passes(self):
        result = self.run_case(self.evidence, self.context)
        self.assertEqual(result["evidence_status"], "valid")
        self.assertEqual(result["control_status"], "pass")
        self.assertTrue(result["policy_executed"])

    def test_near_expiry_certificate_fails(self):
        evidence = dict(self.evidence)
        evidence["observations"] = dict(self.evidence["observations"])
        evidence["observations"]["certificate_not_after_utc"] = "2026-08-05T08:00:00Z"
        result = self.run_case(evidence, self.context)
        self.assertEqual(result["evidence_status"], "valid")
        self.assertEqual(result["control_status"], "fail")
        self.assertTrue(result["policy_executed"])

    def test_mutated_evidence_is_blocked_before_policy(self):
        def mutate(value):
            value["observations"]["public_key_bits"] = 1024
        result = self.run_case(self.evidence, self.context, mutate_after_hash=mutate)
        self.assertEqual(result["evidence_status"], "invalid_evidence")
        self.assertEqual(result["control_status"], "unknown")
        self.assertFalse(result["policy_executed"])

    def test_stale_evidence_is_not_control_failure(self):
        context = dict(self.context)
        context["evaluated_at_utc"] = "2026-08-01T08:00:00Z"
        context["max_evidence_age_hours"] = 24
        result = self.run_case(self.evidence, context)
        self.assertEqual(result["evidence_status"], "stale_evidence")
        self.assertEqual(result["control_status"], "unknown")
        self.assertFalse(result["policy_executed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
