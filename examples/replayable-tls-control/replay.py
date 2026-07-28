from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version", "evidence_id", "evidence_type", "observed_object",
    "source", "collector", "timestamps", "observations", "collection_scope"
}


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


def validate_structure(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - evidence.keys())
    if missing:
        errors.append("missing top-level fields: " + ", ".join(missing))
        return errors
    if evidence.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    if evidence.get("evidence_type") != "tls_certificate_observation":
        errors.append("evidence_type must be tls_certificate_observation")
    collector = evidence.get("collector")
    if not isinstance(collector, dict) or collector.get("mode") != "read_only":
        errors.append("collector.mode must be read_only")
    observations = evidence.get("observations")
    if not isinstance(observations, dict):
        errors.append("observations must be an object")
    else:
        for key in ("certificate_not_after_utc", "public_key_algorithm", "public_key_bits"):
            if key not in observations:
                errors.append(f"observations.{key} is required")
        if not isinstance(observations.get("public_key_bits"), int):
            errors.append("observations.public_key_bits must be an integer")
    try:
        parse_utc(evidence["timestamps"]["collected_at_utc"])
        parse_utc(evidence["observations"]["certificate_not_after_utc"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


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
        [opa_command, "eval", "--format=json", "--data", str(policy), "--stdin-input",
         "data.codeyourcompliance.tls_certificate"],
        input=json.dumps(opa_input), text=True, capture_output=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"OPA failed: {proc.stderr.strip()}")
    payload = json.loads(proc.stdout)
    try:
        value = payload["result"][0]["expressions"][0]["value"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("OPA returned an unexpected result shape") from exc
    allow = bool(value.get("allow", False))
    violations = value.get("violations", [])
    return ("pass" if allow else "fail"), violations


def replay(evidence_path: Path, digest_path: Path, context_path: Path,
           policy_path: Path, policy_engine: str, opa_command: str) -> dict[str, Any]:
    evidence = load_json(evidence_path)
    context = load_json(context_path)
    result: dict[str, Any] = {
        "assessment_schema_version": "0.1.0",
        "evidence_id": evidence.get("evidence_id"),
        "evidence_status": "unknown",
        "control_status": "unknown",
        "policy_executed": False,
        "derived_facts": {},
        "violations": [],
        "gate_trace": []
    }

    schema_errors = validate_structure(evidence)
    if schema_errors:
        result["evidence_status"] = "invalid_evidence"
        result["gate_trace"].append({"gate": "schema", "status": "failed", "errors": schema_errors})
        return result
    result["gate_trace"].append({"gate": "schema", "status": "passed"})

    expected_digest = digest_path.read_text(encoding="utf-8").strip().lower()
    actual_digest = file_sha256(evidence_path)
    if expected_digest != actual_digest:
        result["evidence_status"] = "invalid_evidence"
        result["gate_trace"].append({
            "gate": "integrity", "status": "failed",
            "expected_sha256": expected_digest, "actual_sha256": actual_digest
        })
        return result
    result["gate_trace"].append({"gate": "integrity", "status": "passed", "sha256": actual_digest})

    collected_at = parse_utc(evidence["timestamps"]["collected_at_utc"])
    evaluated_at = parse_utc(context["evaluated_at_utc"])
    max_age_hours = int(context["max_evidence_age_hours"])
    age_hours = (evaluated_at - collected_at).total_seconds() / 3600
    result["derived_facts"]["evidence_age_hours"] = age_hours
    if age_hours < 0 or age_hours > max_age_hours:
        result["evidence_status"] = "stale_evidence"
        result["gate_trace"].append({
            "gate": "freshness", "status": "failed",
            "evidence_age_hours": age_hours, "max_evidence_age_hours": max_age_hours
        })
        return result
    result["gate_trace"].append({"gate": "freshness", "status": "passed"})

    not_after = parse_utc(evidence["observations"]["certificate_not_after_utc"])
    days_to_expiry = int((not_after - evaluated_at).total_seconds() // 86400)
    result["derived_facts"]["days_to_expiry"] = days_to_expiry
    result["evidence_status"] = "valid"

    threshold = int(context["minimum_certificate_days_remaining"])
    opa_input = {
        "evidence": evidence,
        "context": context,
        "derived_facts": result["derived_facts"]
    }
    if policy_engine == "opa":
        control_status, violations = evaluate_opa(policy_path, opa_input, opa_command)
    else:
        control_status, violations = evaluate_builtin(days_to_expiry, threshold)
    result["policy_executed"] = True
    result["control_status"] = control_status
    result["violations"] = violations
    result["gate_trace"].append({"gate": "policy", "status": "executed", "engine": policy_engine})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a TLS evidence package")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--digest", type=Path, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy-engine", choices=("builtin", "opa"), default="builtin")
    parser.add_argument("--opa-command", default="opa")
    args = parser.parse_args()
    try:
        result = replay(args.evidence, args.digest, args.context, args.policy,
                        args.policy_engine, args.opa_command)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"replay failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
