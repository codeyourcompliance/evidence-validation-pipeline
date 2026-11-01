"""Standard-library tests for the offline TLS package closure validator."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_closure import PROFILE, REQUIRED_ROLES, validate  # noqa: E402


class ClosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = {
            "evidence": "input/evidence.json",
            "evidence_digest": "input/evidence.sha256",
            "evidence_schema": "schema/evidence.schema.json",
            "evaluation_context": "input/evaluation-context.json",
            "context_schema": "schema/context.schema.json",
            "policy": "policy/tls_certificate.rego",
            "replay_implementation": "replay.py",
            "runtime_requirements": "requirements.txt",
        }
        self.contents = {role: ("synthetic:" + role + "\n").encode("utf-8") for role in REQUIRED_ROLES}
        self.contents["evidence"] = b'{"source":"synthetic"}\n'
        self.contents["evidence_digest"] = hashlib.sha256(self.contents["evidence"]).hexdigest().encode() + b"\n"
        self.manifest = {"manifest_version": "0.1.0", "profile": PROFILE, "artifacts": []}
        for role in REQUIRED_ROLES:
            name = self.paths[role]
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(self.contents[role])
            self.manifest["artifacts"].append({"role": role, "path": name, "sha256": self.hash(dest)})
        self.write_manifest()

    @staticmethod
    def hash(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_manifest(self) -> None:
        (self.root / "closure-manifest.json").write_text(json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8")

    def run_validator(self):
        return validate(self.root / "closure-manifest.json")

    def codes(self):
        return {x["code"] for x in self.run_validator()["issues"]}

    def test_complete_package(self):
        result = self.run_validator()
        self.assertEqual(result["closure_status"], "satisfied")
        self.assertEqual(len(result["checks"]), len(REQUIRED_ROLES))
        self.assertFalse(result["issues"])
        self.assertTrue(all(x["status"] == "sha256_match" for x in result["checks"]))
        self.assertFalse(result["replay_executed"])
        self.assertFalse(result["decision_executed"])
        self.assertEqual(result["control_status"], "unknown")
        self.assertEqual(result["manifest_authentication_status"], "not_assessed")
        self.assertEqual(result["runtime_availability_status"], "not_assessed")

    def test_missing_required_role(self):
        self.manifest["artifacts"] = [x for x in self.manifest["artifacts"] if x["role"] != "policy"]
        self.write_manifest()
        self.assertIn("missing_required_role", self.codes())

    def test_missing_file(self):
        (self.root / self.paths["policy"]).unlink()
        self.assertIn("missing_or_not_file", self.codes())

    def test_tampered_file(self):
        (self.root / self.paths["policy"]).write_text("changed policy\n", encoding="utf-8")
        self.assertIn("sha256_mismatch", self.codes())

    def test_digest_file_binding_mismatch(self):
        file = self.root / self.paths["evidence_digest"]
        file.write_text("0" * 64 + "\n", encoding="ascii")
        for entry in self.manifest["artifacts"]:
            if entry["role"] == "evidence_digest":
                entry["sha256"] = self.hash(file)
        self.write_manifest()
        self.assertIn("evidence_digest_binding_mismatch", self.codes())
        self.assertTrue(all(x["status"] == "sha256_match" for x in self.run_validator()["checks"]))

    def test_invalid_digest_file_encoding_or_format(self):
        file = self.root / self.paths["evidence_digest"]
        file.write_bytes(b"not-a-digest\n")
        for entry in self.manifest["artifacts"]:
            if entry["role"] == "evidence_digest":
                entry["sha256"] = self.hash(file)
        self.write_manifest()
        self.assertIn("evidence_digest_binding_mismatch", self.codes())

    def test_path_traversal(self):
        self.manifest["artifacts"][0]["path"] = "../elsewhere/evidence.json"
        self.write_manifest()
        self.assertIn("invalid_path", self.codes())

    def test_absolute_windows_drive_and_backslash_rejected(self):
        for path in ("/etc/passwd", "C:/Windows/win.ini", r"..\evidence.json", "input//evidence.json", "input/./evidence.json"):
            with self.subTest(path=path):
                self.manifest["artifacts"][0]["path"] = path
                self.write_manifest()
                self.assertIn("invalid_path", self.codes())

    def test_windows_reserved_file_rejected(self):
        self.manifest["artifacts"][0]["path"] = "input/CON.txt"
        self.write_manifest()
        self.assertIn("invalid_path", self.codes())

    def test_duplicate_roles(self):
        self.manifest["artifacts"][1]["role"] = "evidence"
        self.write_manifest()
        self.assertIn("duplicate_role", self.codes())

    def test_case_insensitive_duplicate_paths(self):
        self.manifest["artifacts"][1]["path"] = "INPUT/EVIDENCE.JSON"
        self.write_manifest()
        self.assertIn("duplicate_path", self.codes())

    def test_unknown_role(self):
        self.manifest["artifacts"][0]["role"] = "optional_magic"
        self.write_manifest()
        self.assertIn("unknown_role", self.codes())

    def test_bad_digest(self):
        self.manifest["artifacts"][0]["sha256"] = "sha256:FAKE"
        self.write_manifest()
        self.assertIn("invalid_sha256", self.codes())

    def test_unknown_profile(self):
        self.manifest["profile"] = "custom-loose"
        self.write_manifest()
        self.assertIn("unsupported_profile_or_version", self.codes())

    def test_duplicate_json_key(self):
        text = (self.root / "closure-manifest.json").read_text(encoding="utf-8")
        text = text.replace('"profile": "tls-replay-v0.1",', '"profile": "tls-replay-v0.1", "profile": "tls-replay-v0.1",')
        (self.root / "closure-manifest.json").write_text(text, encoding="utf-8")
        self.assertIn("manifest_read_or_parse_error", self.codes())

    def test_symlink_dependency_is_blocked(self):
        link = self.root / self.paths["policy"]
        target = self.root / "policy/real.rego"
        target.write_bytes(link.read_bytes())
        link.unlink()
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        self.assertIn("symlink_disallowed", self.codes())

    def test_missing_manifest_is_blocked(self):
        (self.root / "closure-manifest.json").unlink()
        self.assertIn("manifest_read_or_parse_error", self.codes())

    def test_read_only_and_deterministic(self):
        before = {p.relative_to(self.root).as_posix(): self.hash(p) for p in self.root.rglob("*") if p.is_file()}
        one, two = self.run_validator(), self.run_validator()
        after = {p.relative_to(self.root).as_posix(): self.hash(p) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(one, two)
        self.assertEqual(before, after)

    def test_cli_exit_codes(self):
        command = [sys.executable, str(ROOT / "tools/validate_closure.py"), "--manifest", str(self.root / "closure-manifest.json")]
        good = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(good.returncode, 0)
        self.assertEqual(json.loads(good.stdout)["closure_status"], "satisfied")
        (self.root / self.paths["policy"]).unlink()
        bad = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(json.loads(bad.stdout)["closure_status"], "blocked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
