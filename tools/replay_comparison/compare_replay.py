"""Bounded TLS replay comparison. Does not authenticate the recorded baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "evidence_package_closure"))
from validate_closure import PROFILE, REQUIRED_ROLES, validate as validate_closure  # noqa: E402

HEX64 = re.compile(r"[0-9a-f]{64}\Z")
RUNNER_ARTIFACTS = ("evidence", "evidence_schema", "evaluation_context", "context_schema", "policy")
DECISION_FIELDS = ("evidence_id", "evidence_status", "context_status", "control_status", "violations", "derived_facts")
RECORDED_FIELDS = set(DECISION_FIELDS) | {"decision_engine", "decision_executed", "policy_artifact_executed", "implementation_name", "implementation_version"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load_json(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys)
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object")
    return value, sha256(raw)


def typed_json_equal(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's bool/number equality coercion."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            typed_json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            typed_json_equal(l_item, r_item) for l_item, r_item in zip(left, right)
        )
    return left == right


def valid_baseline(value: dict[str, Any]) -> bool:
    if set(value) != {"record_type", "profile", "authority", "artifact_sha256", "recorded"}:
        return False
    if value["record_type"] != "synthetic_tls_recorded_assessment_v0.1" or value["profile"] != PROFILE:
        return False
    if value["authority"] != "unattested_synthetic_fixture":
        return False
    bindings = value["artifact_sha256"]
    if not isinstance(bindings, dict) or set(bindings) != set(REQUIRED_ROLES):
        return False
    if any(not isinstance(h, str) or not HEX64.fullmatch(h) for h in bindings.values()):
        return False
    r = value["recorded"]
    if not isinstance(r, dict) or set(r) != RECORDED_FIELDS:
        return False
    return (r["decision_engine"] in ("builtin", "opa")
            and type(r["decision_executed"]) is bool and r["decision_executed"]
            and type(r["policy_artifact_executed"]) is bool
            and r["policy_artifact_executed"] == (r["decision_engine"] == "opa")
            and r["control_status"] in ("pass", "fail")
            and r["evidence_status"] == "valid" and r["context_status"] == "valid"
            and isinstance(r["evidence_id"], str) and bool(r["evidence_id"])
            and isinstance(r["violations"], list) and isinstance(r["derived_facts"], dict)
            and r["implementation_name"] == "codeyourcompliance.replayable_tls_control"
            and isinstance(r["implementation_version"], str) and bool(r["implementation_version"]))


def receipt() -> dict[str, Any]:
    return {
        "receipt_version": "0.1.0",
        "profile": PROFILE,
        "comparison_status": "blocked",
        "closure_status": "blocked",
        "reason_codes": [],
        "mismatched_fields": [],
        "recorded_baseline_sha256": None,
        "manifest_sha256": None,
        "recorded_result": None,
        "replayed_result": None,
        "runner_invoked": False,
        "decision_executed": False,
        "policy_artifact_executed": False,
        "baseline_authentication": "not_assessed",
        "manifest_authentication": "not_assessed",
        "runtime_equivalence": "not_assessed",
        "historical_replay_verified": False,
    }


def compare(manifest_path: Path, recorded_path: Path, engine: str, opa_command: str = "opa") -> dict[str, Any]:
    out = receipt()
    try:
        baseline, out["recorded_baseline_sha256"] = load_json(recorded_path)
        if not valid_baseline(baseline):
            out["reason_codes"].append("invalid_recorded_baseline")
            return out
        manifest, out["manifest_sha256"] = load_json(manifest_path)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        out["reason_codes"].append("unreadable_or_invalid_input")
        return out

    out["recorded_result"] = baseline["recorded"]["control_status"]
    closure = validate_closure(manifest_path)
    out["closure_status"] = closure["closure_status"]
    if closure["closure_status"] != "satisfied":
        out["reason_codes"] = ["closure_blocked"] + sorted({i["code"] for i in closure["issues"]})
        return out

    if engine not in ("builtin", "opa"):
        out["reason_codes"].append("unsupported_engine")
        return out

    current_bindings = {item["role"]: item["sha256"] for item in manifest["artifacts"]}
    mismatched = sorted(role for role in REQUIRED_ROLES if baseline["artifact_sha256"][role] != current_bindings[role])
    if mismatched:
        out["comparison_status"] = "input_mismatch"
        out["reason_codes"].append("artifact_binding_mismatch")
        out["mismatched_fields"] = ["artifact_sha256." + role for role in mismatched]
        return out
    if baseline["recorded"]["decision_engine"] != engine:
        out["comparison_status"] = "input_mismatch"
        out["reason_codes"].append("engine_mismatch")
        out["mismatched_fields"].append("decision_engine")
        return out

    package = manifest_path.parent
    paths = {item["role"]: package / item["path"] for item in manifest["artifacts"]}
    with tempfile.TemporaryDirectory() as tmp:
        result_path = Path(tmp) / "replayed-assessment.json"
        cmd = [sys.executable, str(paths["replay_implementation"]),
               "--evidence", str(paths["evidence"]),
               "--digest", str(paths["evidence_digest"]),
               "--context", str(paths["evaluation_context"]),
               "--evidence-schema", str(paths["evidence_schema"]),
               "--context-schema", str(paths["context_schema"]),
               "--policy", str(paths["policy"]),
               "--output", str(result_path), "--policy-engine", engine,
               "--opa-command", opa_command]
        out["runner_invoked"] = True
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
            if proc.returncode != 0:
                out["reason_codes"].append("replay_process_failed")
                return out
            actual, _ = load_json(result_path)
        except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired):
            out["reason_codes"].append("replay_output_unavailable")
            return out

    # The package may have changed between preflight and runner execution.
    if validate_closure(manifest_path)["closure_status"] != "satisfied":
        out["reason_codes"].append("closure_changed_during_execution")
        return out
    if (type(actual.get("decision_executed")) is not bool
            or not isinstance(actual.get("policy_artifact"), dict)
            or type(actual["policy_artifact"].get("executed")) is not bool):
        out["reason_codes"].append("invalid_replay_result")
        return out
    out["decision_executed"] = actual["decision_executed"]
    out["policy_artifact_executed"] = actual["policy_artifact"]["executed"]
    out["replayed_result"] = actual.get("control_status")
    if not out["decision_executed"] or actual.get("control_status") not in ("pass", "fail"):
        out["reason_codes"].append("decision_not_executed")
        return out
    if (not isinstance(actual.get("artifacts"), dict)
            or not isinstance(actual.get("derived_facts"), dict)
            or not isinstance(actual.get("violations"), list)
            or not isinstance(actual.get("evidence_id"), str)):
        out["reason_codes"].append("invalid_replay_result")
        return out
    for role in RUNNER_ARTIFACTS:
        item = actual["artifacts"].get(role)
        if not isinstance(item, dict) or item.get("sha256") != current_bindings[role]:
            out["mismatched_fields"].append("replayed_artifacts." + role)
    if out["mismatched_fields"]:
        out["comparison_status"] = "input_mismatch"
        out["reason_codes"].append("replay_input_binding_mismatch")
        return out

    expected = baseline["recorded"]
    context = actual.get("implementation")
    if not isinstance(context, dict):
        out["reason_codes"].append("invalid_implementation_metadata")
        return out
    provenance = {
        "decision_engine": actual.get("decision_engine"),
        "policy_artifact_executed": actual["policy_artifact"]["executed"],
        "implementation_name": context.get("name"),
        "implementation_version": context.get("version"),
    }
    out["mismatched_fields"] = sorted(key for key, value in provenance.items() if value != expected[key])
    if actual["policy_artifact"].get("engine") != expected["decision_engine"]:
        out["mismatched_fields"].append("policy_artifact.engine")
    if out["mismatched_fields"]:
        out["comparison_status"] = "input_mismatch"
        out["reason_codes"].append("evaluation_provenance_mismatch")
        return out
    out["mismatched_fields"] = sorted(key for key in DECISION_FIELDS
                                      if not typed_json_equal(actual.get(key), expected[key]))
    if out["mismatched_fields"]:
        out["comparison_status"] = "decision_mismatch"
        out["reason_codes"].append("result_difference")
        return out

    out["comparison_status"] = "matched"
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute and compare a bounded synthetic TLS replay")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--recorded", required=True, type=Path)
    parser.add_argument("--engine", choices=("builtin", "opa"), default="builtin")
    parser.add_argument("--opa-command", default="opa")
    parser.add_argument("--output", type=Path, help="New receipt file outside the evidence package")
    args = parser.parse_args()
    if args.output:
        package = args.manifest.resolve().parent
        if args.output.resolve() == package or package in args.output.resolve().parents:
            parser.error("output receipt must be outside the evidence package")
        if args.output.exists():
            parser.error("output receipt must not overwrite an existing file")
    result = compare(args.manifest, args.recorded, args.engine, args.opa_command)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8", newline="\n") as file:
                file.write(rendered)
        except OSError as exc:
            parser.error("cannot write new receipt: " + str(exc))
    print(rendered, end="")
    return {"matched": 0, "input_mismatch": 1, "decision_mismatch": 1, "blocked": 2}[result["comparison_status"]]


if __name__ == "__main__":
    raise SystemExit(main())
