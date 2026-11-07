"""Synthetic TLS replay receipt tests; no network, target, or OPA needed."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_replay import compare  # noqa: E402

PATHS = {
    "evidence": "input/evidence.json",
    "evidence_digest": "input/evidence.sha256",
    "evidence_schema": "schema/evidence.schema.json",
    "evaluation_context": "input/evaluation-context.json",
    "context_schema": "schema/context.schema.json",
    "policy": "policy/tls_certificate.rego",
    "replay_implementation": "replay.py",
    "runtime_requirements": "requirements.txt",
}

# Minimal fake of the existing TLS replay's CLI/output contract.
# This script is executed in a subprocess so the wrapper's invocation is tested.
FAKE_RUNNER = '''import argparse, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser()
for name in ('evidence','digest','context','evidence-schema','context-schema','policy','output','policy-engine','opa-command'):
    p.add_argument('--'+name)
a=p.parse_args()
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
e=json.loads(Path(a.evidence).read_text())
c=json.loads(Path(a.context).read_text())
result={'assessment_schema_version':'0.1.0','evidence_id':e['evidence_id'],
 'evidence_status':'valid','context_status':'valid','control_status':'pass',
 'decision_executed':True,'decision_engine':a.policy_engine,
 'policy_artifact':{'engine':a.policy_engine,'executed':a.policy_engine=='opa'},
 'violations':[],'derived_facts':{'days_to_expiry':64,'evidence_age_hours':0.0},
 'implementation':{'name':'codeyourcompliance.replayable_tls_control','version':'0.1.1',
                   'python_version':'test-runtime','opa_version':None},
 'artifacts':{r:{'sha256':digest(getattr(a,n))} for r,n in (
     ('evidence','evidence'),('evaluation_context','context'),('evidence_schema','evidence_schema'),
     ('context_schema','context_schema'),('policy','policy'))}}
if c.get('force_block'):
    result['decision_executed']=False
    result['control_status']='unknown'
if c.get('force_fail'):
    result['control_status']='fail'
if c.get('force_binding_mismatch'):
    result['artifacts']['policy']['sha256']='0'*64
if c.get('force_engine_mismatch'):
    result['policy_artifact']['engine']='opa'
Path(a.output).write_text(json.dumps(result),encoding='utf-8')
print(json.dumps(result))
'''


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ReplayComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "package"
        self.package.mkdir()
        self.baseline_path = self.root / "recorded.json"
        self.manifest_path = self.package / "closure-manifest.json"
        self.contents = {
            "evidence": b'{"evidence_id":"ev-tls-example-001"}\n',
            "evaluation_context": b'{"evaluated_at_utc":"2026-07-28T08:00:00Z"}\n',
            "evidence_schema": b'{}\n',
            "context_schema": b'{}\n',
            "policy": b'package codeyourcompliance.tls_certificate\n',
            "replay_implementation": FAKE_RUNNER.encode("utf-8"),
            "runtime_requirements": b'jsonschema>=4.24,<5\n',
        }
        self.contents["evidence_digest"] = digest(self.contents["evidence"]).encode() + b"\n"
        self.manifest = {"manifest_version": "0.1.0", "profile": "tls-replay-v0.1", "artifacts": []}
        for role, relative in PATHS.items():
            target = self.package / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.contents[role])
            self.manifest["artifacts"].append({"role": role, "path": relative, "sha256": digest(self.contents[role])})
        self.write_manifest()
        self.baseline = {
            "record_type": "synthetic_tls_recorded_assessment_v0.1",
            "profile": "tls-replay-v0.1",
            "authority": "unattested_synthetic_fixture",
            "artifact_sha256": {role: digest(blob) for role, blob in self.contents.items()},
            "recorded": {
                "evidence_id": "ev-tls-example-001",
                "evidence_status": "valid",
                "context_status": "valid",
                "control_status": "pass",
                "decision_engine": "builtin",
                "decision_executed": True,
                "policy_artifact_executed": False,
                "implementation_name": "codeyourcompliance.replayable_tls_control",
                "implementation_version": "0.1.1",
                "violations": [],
                "derived_facts": {"days_to_expiry": 64, "evidence_age_hours": 0.0},
            },
        }
        self.write_baseline()

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8")

    def write_baseline(self):
        self.baseline_path.write_text(json.dumps(self.baseline, indent=2) + "\n", encoding="utf-8")

    def test_matched_executes_runner_and_keeps_authentication_unassessed(self):
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "matched", out)
        self.assertTrue(out["runner_invoked"])
        self.assertTrue(out["decision_executed"])
        self.assertFalse(out["policy_artifact_executed"])
        self.assertFalse(out["historical_replay_verified"])
        self.assertEqual(out["baseline_authentication"], "not_assessed")
        self.assertEqual(out["runtime_equivalence"], "not_assessed")

    def test_binding_mismatch_blocks_before_runner(self):
        self.baseline["artifact_sha256"]["evaluation_context"] = "0" * 64
        self.write_baseline()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "input_mismatch")
        self.assertFalse(out["runner_invoked"])
        self.assertIn("artifact_sha256.evaluation_context", out["mismatched_fields"])

    def test_same_recorded_pass_but_policy_binding_different_blocks(self):
        self.baseline["artifact_sha256"]["policy"] = "f" * 64
        self.write_baseline()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "input_mismatch")
        self.assertFalse(out["runner_invoked"])

    def test_decision_mismatch_detected_after_runner(self):
        self.baseline["recorded"]["control_status"] = "fail"
        self.write_baseline()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "decision_mismatch", out)
        self.assertTrue(out["runner_invoked"])
        self.assertIn("control_status", out["mismatched_fields"])

    def test_engine_mismatch_does_not_run_other_engine(self):
        out = compare(self.manifest_path, self.baseline_path, "opa")
        self.assertEqual(out["comparison_status"], "input_mismatch")
        self.assertIn("engine_mismatch", out["reason_codes"])
        self.assertFalse(out["runner_invoked"])

    def test_missing_required_file_blocks_with_no_control_fail(self):
        (self.package / PATHS["policy"]).unlink()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "blocked")
        self.assertFalse(out["runner_invoked"])
        self.assertFalse(out["decision_executed"])
        self.assertIsNone(out["replayed_result"])

    def test_modified_file_blocks_closure_even_with_recorded_pass(self):
        (self.package / PATHS["evidence"]).write_text("tampered\n")
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "blocked")
        self.assertIn("closure_blocked", out["reason_codes"])

    def test_blocked_policy_decision_is_not_decision_mismatch(self):
        context = self.package / PATHS["evaluation_context"]
        context.write_text('{"force_block":true}')
        new_sha = digest(context.read_bytes())
        self.baseline["artifact_sha256"]["evaluation_context"] = new_sha
        for entry in self.manifest["artifacts"]:
            if entry["role"] == "evaluation_context": entry["sha256"] = new_sha
        self.write_manifest()
        self.write_baseline()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "blocked", out)
        self.assertTrue(out["runner_invoked"])
        self.assertFalse(out["decision_executed"])
        self.assertIn("decision_not_executed", out["reason_codes"])

    def adjust_context(self, value):
        context = self.package / PATHS["evaluation_context"]
        context.write_text(json.dumps(value), encoding="utf-8")
        new_sha = digest(context.read_bytes())
        self.baseline["artifact_sha256"]["evaluation_context"] = new_sha
        for entry in self.manifest["artifacts"]:
            if entry["role"] == "evaluation_context": entry["sha256"] = new_sha
        self.write_manifest()
        self.write_baseline()

    def test_runner_reported_input_hash_mismatch(self):
        self.adjust_context({"force_binding_mismatch": True})
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "input_mismatch", out)
        self.assertTrue(out["runner_invoked"])
        self.assertIn("replayed_artifacts.policy", out["mismatched_fields"])

    def test_runner_reported_engine_identity_mismatch(self):
        self.adjust_context({"force_engine_mismatch": True})
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "input_mismatch", out)
        self.assertIn("policy_artifact.engine", out["mismatched_fields"])

    def test_read_only_and_stable_receipt(self):
        before = {p.relative_to(self.package).as_posix(): digest(p.read_bytes())
                  for p in self.package.rglob("*") if p.is_file()}
        first = compare(self.manifest_path, self.baseline_path, "builtin")
        second = compare(self.manifest_path, self.baseline_path, "builtin")
        after = {p.relative_to(self.package).as_posix(): digest(p.read_bytes())
                 for p in self.package.rglob("*") if p.is_file()}
        self.assertEqual(first, second)
        self.assertEqual(before, after)

    def test_duplicate_baseline_key_blocks(self):
        text = self.baseline_path.read_text()
        self.baseline_path.write_text(text.replace('"profile": "tls-replay-v0.1",',
                         '"profile": "tls-replay-v0.1", "profile": "tls-replay-v0.1",'))
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "blocked")
        self.assertIn("unreadable_or_invalid_input", out["reason_codes"])

    def test_nonexecuted_recorded_baseline_rejected(self):
        self.baseline["recorded"]["decision_executed"] = False
        self.write_baseline()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "blocked")
        self.assertIn("invalid_recorded_baseline", out["reason_codes"])

    def test_runner_failure_blocks_without_fabricated_decision(self):
        runner = self.package / PATHS["replay_implementation"]
        runner.write_text("raise RuntimeError('synthetic failure')\n")
        new_sha = digest(runner.read_bytes())
        self.baseline["artifact_sha256"]["replay_implementation"] = new_sha
        for entry in self.manifest["artifacts"]:
            if entry["role"] == "replay_implementation": entry["sha256"] = new_sha
        self.write_baseline()
        self.write_manifest()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "blocked")
        self.assertIn("replay_process_failed", out["reason_codes"])

    def test_cli_reports_matched_and_blocks_writes_into_package(self):
        script = Path(__file__).resolve().parents[1] / "compare_replay.py"
        proc = subprocess.run([sys.executable, str(script), "--manifest", str(self.manifest_path),
                               "--recorded", str(self.baseline_path), "--engine", "builtin"],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["comparison_status"], "matched")
        unsafe = subprocess.run([sys.executable, str(script), "--manifest", str(self.manifest_path),
                                "--recorded", str(self.baseline_path), "--output", str(self.package / "receipt.json")],
                               capture_output=True, text=True, check=False)
        self.assertNotEqual(unsafe.returncode, 0)
        self.assertFalse((self.package / "receipt.json").exists())

    def test_same_inputs_different_decision_not_control_drift(self):
        self.baseline["recorded"]["violations"] = [{"code":"EXPECTED_DIFFERENT"}]
        self.write_baseline()
        out = compare(self.manifest_path, self.baseline_path, "builtin")
        self.assertEqual(out["comparison_status"], "decision_mismatch")
        self.assertIn("violations", out["mismatched_fields"])
        self.assertFalse(out["historical_replay_verified"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
