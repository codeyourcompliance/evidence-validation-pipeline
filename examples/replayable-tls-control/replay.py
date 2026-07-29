from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

IMPLEMENTATION_VERSION = "0.1.1"
OPA_ENTRYPOINT = "data.codeyourcompliance.tls_certificate"


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"timestamp must be UTC and end with Z: {value!r}")
    return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_instance(instance: dict[str, Any], schema_path: Path) -> list[str]:
    validator = Draft202012Validator(load_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    rendered: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path) or "$"
        rendered.append(f"{path}: {error.message}")
    return rendered


def opa_version(opa_command: str) -> str | None:
    if shutil.which(opa_command) is None:
        return None
    proc = subprocess.run([opa_command, "version"], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return None
    lines = proc.stdout.strip().splitlines()
    return lines[0] if lines else None


def evaluate_builtin(days_to_expiry: int, threshold: int) -> tuple[str, list[dict[str, Any]]]:
    if days_to_expiry >= threshold:
        return "pass", []
    return "fail", [{
        "code": "TLS_CERTIFICATE_EXPIRY_THRESHOLD",
        "message": f"certificate has {days_to_expiry} days remaining; minimum is {threshold}"
    }]


def evaluate_opa(policy: Path, opa_input: dict[str, Any], opa_command: str) -> tuple[str, list[dict[str, Any]]]:
    if shutil.which(opa_command) is None:
        raise RuntimeError(f"OPA executable not found: {opa_command}")
    proc = subprocess.run(
        [opa_command, "eval", "--format=json", "--data", str(policy), "--stdin-input", OPA_ENTRYPOINT],
        input=json.dumps(opa_input), text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"OPA failed: {proc.stderr.strip()}")
    payload = json.loads(proc.stdout)
    try:
        value = payload["result"][0]["expressions"][0]["value"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("OPA returned an unexpected result shape") from exc
    if not isinstance(value, dict):
        raise RuntimeError("OPA entrypoint did not return an object")
    allow = value.get("allow", False)
    violations = value.get("violations", [])
    if not isinstance(allow, bool) or not isinstance(violations, list):
        raise RuntimeError("OPA result shape is invalid")
    return ("pass" if allow else "fail"), violations


def replay(evidence_path: Path, digest_path: Path, context_path: Path,
           evidence_schema_path: Path, context_schema_path: Path,
           policy_path: Path, policy_engine: str, opa_command: str) -> dict[str, Any]:
    evidence = load_json(evidence_path)
    context = load_json(context_path)
    result: dict[str, Any] = {
        "assessment_schema_version": "0.1.0",
        "implementation": {
            "name": "codeyourcompliance.replayable_tls_control",
            "version": IMPLEMENTATION_VERSION,
            "python_version": platform.python_version(),
            "opa_version": opa_version(opa_command) if policy_engine == "opa" else None,
        },
        "artifacts": {
            "evidence": {"path": str(evidence_path), "sha256": file_sha256(evidence_path)},
            "evidence_schema": {"path": str(evidence_schema_path), "sha256": file_sha256(evidence_schema_path)},
            "evaluation_context": {"path": str(context_path), "sha256": file_sha256(context_path)},
            "context_schema": {"path": str(context_schema_path), "sha256": file_sha256(context_schema_path)},
            "policy": {"path": str(policy_path), "sha256": file_sha256(policy_path), "entrypoint": OPA_ENTRYPOINT},
        },
        "evidence_id": evidence.get("evidence_id"),
        "evidence_status": "unknown",
        "context_status": "unknown",
        "control_status": "unknown",
        "decision_engine": policy_engine,
        "decision_executed": False,
        "policy_artifact": {"executed": False, "engine": policy_engine},
        "derived_facts": {},
        "violations": [],
        "gate_trace": [],
    }

    evidence_errors = validate_instance(evidence, evidence_schema_path)
    if evidence_errors:
        result["evidence_status"] = "invalid_evidence"
        result["gate_trace"].append({"gate": "evidence_schema", "status": "failed", "errors": evidence_errors})
        return result
    result["gate_trace"].append({"gate": "evidence_schema", "status": "passed"})

    context_errors = validate_instance(context, context_schema_path)
    if context_errors:
        result["context_status"] = "invalid_context"
        result["gate_trace"].append({"gate": "context_schema", "status": "failed", "errors": context_errors})
        return result
    result["context_status"] = "valid"
    result["gate_trace"].append({"gate": "context_schema", "status": "passed"})

    expected_digest = digest_path.read_text(encoding="utf-8").strip().lower()
    actual_digest = file_sha256(evidence_path)
    if expected_digest != actual_digest:
        result["evidence_status"] = "invalid_evidence"
        result["gate_trace"].append({
            "gate": "integrity", "status": "failed",
            "expected_sha256": expected_digest, "actual_sha256": actual_digest,
        })
        return result
    result["gate_trace"].append({"gate": "integrity", "status": "passed", "sha256": actual_digest})

    collected_at = parse_utc(evidence["timestamps"]["collected_at_utc"])
    evaluated_at = parse_utc(context["evaluated_at_utc"])
    max_age_hours = float(context["max_evidence_age_hours"])
    age_hours = (evaluated_at - collected_at).total_seconds() / 3600
    result["derived_facts"]["evidence_age_hours"] = age_hours
    if age_hours < 0 or age_hours > max_age_hours:
        result["evidence_status"] = "stale_evidence"
        result["gate_trace"].append({
            "gate": "freshness", "status": "failed",
            "evidence_age_hours": age_hours, "max_evidence_age_hours": max_age_hours,
        })
        return result
    result["gate_trace"].append({"gate": "freshness", "status": "passed", "evidence_age_hours": age_hours})

    not_after = parse_utc(evidence["observations"]["certificate_not_after_utc"])
    days_to_expiry = int((not_after - evaluated_at).total_seconds() // 86400)
    result["derived_facts"]["days_to_expiry"] = days_to_expiry
    result["evidence_status"] = "valid"

    threshold = context["minimum_certificate_days_remaining"]
    opa_input = {"evidence": evidence, "context": context, "derived_facts": result["derived_facts"]}
    if policy_engine == "opa":
        control_status, violations = evaluate_opa(policy_path, opa_input, opa_command)
        result["policy_artifact"]["executed"] = True
    else:
        control_status, violations = evaluate_builtin(days_to_expiry, threshold)

    result["decision_executed"] = True
    result["control_status"] = control_status
    result["violations"] = violations
    result["gate_trace"].append({
        "gate": "decision", "status": "executed", "engine": policy_engine,
        "policy_artifact_executed": result["policy_artifact"]["executed"],
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a TLS evidence package")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--digest", type=Path, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--evidence-schema", type=Path, required=True)
    parser.add_argument("--context-schema", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy-engine", choices=("builtin", "opa"), default="builtin")
    parser.add_argument("--opa-command", default="opa")
    args = parser.parse_args()
    try:
        result = replay(args.evidence, args.digest, args.context, args.evidence_schema,
                        args.context_schema, args.policy, args.policy_engine, args.opa_command)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"replay failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
