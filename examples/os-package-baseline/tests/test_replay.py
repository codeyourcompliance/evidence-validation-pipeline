from __future__ import annotations

import hashlib
import json
import shutil
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
        self.policy = ROOT / "policy/package_baseline.rego"
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

    def test_baseline_match_passes(self):
        result = self.run_case(self.evidence, self.context)
        self.assertEqual(result["control_status"], "pass")
        self.assertTrue(result["decision_executed"])

    def test_missing_required_package_fails(self):
        evidence = json.loads(json.dumps(self.evidence))
        evidence["observations"]["packages"] = [p for p in evidence["observations"]["packages"] if p["name"] != "curl"]
        result = self.run_case(evidence, self.context)
        self.assertEqual(result["control_status"], "fail")
        self.assertEqual(result["violations"][0]["code"], "MISSING_REQUIRED_PACKAGE")

    def test_version_mismatch_fails(self):
        evidence = json.loads(json.dumps(self.evidence))
        evidence["observations"]["packages"][0]["version"] = "1.1.1"
        result = self.run_case(evidence, self.context)
        self.assertEqual(result["control_status"], "fail")
        self.assertEqual(result["violations"][0]["code"], "PACKAGE_VERSION_MISMATCH")

    def test_unexpected_package_is_configurable(self):
        evidence = json.loads(json.dumps(self.evidence))
        evidence["observations"]["packages"].append({"name": "telnet", "version": "0.17"})
        ignored = self.run_case(evidence, self.context)
        self.assertEqual(ignored["control_status"], "pass")
        context = dict(self.context)
        context["unexpected_package_mode"] = "fail"
        blocked = self.run_case(evidence, context)
        self.assertEqual(blocked["control_status"], "fail")
        self.assertEqual(blocked["violations"][0]["code"], "UNEXPECTED_PACKAGE")

    def test_stale_evidence_is_unknown(self):
        context = dict(self.context)
        context["evaluated_at_utc"] = "2026-08-01T08:00:00Z"
        result = self.run_case(self.evidence, context)
        self.assertEqual(result["evidence_status"], "stale_evidence")
        self.assertEqual(result["control_status"], "unknown")
        self.assertFalse(result["decision_executed"])

    def test_mutated_evidence_is_blocked(self):
        result = self.run_case(self.evidence, self.context, mutate_after_hash=lambda value: value["observations"]["packages"].clear())
        self.assertEqual(result["evidence_status"], "invalid_evidence")
        self.assertFalse(result["decision_executed"])

    def test_invalid_context_is_separate(self):
        context = dict(self.context)
        context["max_evidence_age_hours"] = -1
        result = self.run_case(self.evidence, context)
        self.assertEqual(result["context_status"], "invalid_context")
        self.assertEqual(result["evidence_status"], "unknown")

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
