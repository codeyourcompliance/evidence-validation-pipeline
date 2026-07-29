from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from replay import replay

ROOT = Path(__file__).resolve().parents[1]
STABLE_FIELDS = (
    "evidence_status", "context_status", "control_status", "decision_engine",
    "decision_executed", "policy_artifact", "violations",
)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads((ROOT / "input/evidence.json").read_text(encoding="utf-8"))
        self.context = json.loads((ROOT / "input/evaluation-context.json").read_text(encoding="utf-8"))
        self.policy = ROOT / "policy/tls_certificate.rego"
        self.evidence_schema = ROOT / "schema/evidence.schema.json"
        self.context_schema = ROOT / "schema/context.schema.json"

    def run_case(self, evidence: dict, context: dict, engine: str = "builtin", mutate_after_hash=None):
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
            return replay(evidence_path, digest_path, context_path, self.evidence_schema,
                          self.context_schema, self.policy, engine, "opa")

    def assert_expected(self, result: dict, name: str) -> None:
        expected = json.loads((ROOT / f"expected/{name}.json").read_text(encoding="utf-8"))
        actual = {field: result[field] for field in STABLE_FIELDS}
        self.assertEqual(actual, expected)

    def test_valid_safe_certificate_passes(self):
        self.assert_expected(self.run_case(self.evidence, self.context), "pass")

    def test_near_expiry_certificate_fails(self):
        evidence = json.loads(json.dumps(self.evidence))
        evidence["observations"]["certificate_not_after_utc"] = "2026-08-05T08:00:00Z"
        self.assert_expected(self.run_case(evidence, self.context), "fail")

    def test_mutated_evidence_is_blocked_before_decision(self):
        def mutate(value):
            value["observations"]["public_key_bits"] = 1024
        self.assert_expected(self.run_case(self.evidence, self.context, mutate_after_hash=mutate), "invalid_evidence")

    def test_stale_evidence_is_not_control_failure(self):
        context = dict(self.context)
        context["evaluated_at_utc"] = "2026-08-01T08:00:00Z"
        self.assert_expected(self.run_case(self.evidence, context), "stale_evidence")

    def test_invalid_context_is_separate_from_invalid_evidence(self):
        context = dict(self.context)
        context["max_evidence_age_hours"] = -1
        result = self.run_case(self.evidence, context)
        self.assertEqual(result["evidence_status"], "unknown")
        self.assertEqual(result["context_status"], "invalid_context")
        self.assertEqual(result["control_status"], "unknown")
        self.assertFalse(result["decision_executed"])

    def test_schema_rejects_boolean_public_key_bits(self):
        evidence = json.loads(json.dumps(self.evidence))
        evidence["observations"]["public_key_bits"] = True
        result = self.run_case(evidence, self.context)
        self.assertEqual(result["evidence_status"], "invalid_evidence")
        self.assertFalse(result["decision_executed"])

    @unittest.skipUnless(shutil.which("opa"), "OPA executable is not installed")
    def test_builtin_and_opa_are_semantically_equivalent(self):
        builtin = self.run_case(self.evidence, self.context, engine="builtin")
        opa = self.run_case(self.evidence, self.context, engine="opa")
        self.assertEqual(builtin["control_status"], opa["control_status"])
        self.assertEqual(builtin["violations"], opa["violations"])
        self.assertEqual(builtin["derived_facts"], opa["derived_facts"])
        self.assertFalse(builtin["policy_artifact"]["executed"])
        self.assertTrue(opa["policy_artifact"]["executed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
