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

IMPLEMENTATION_VERSION = "0.1.0"
OPA_ENTRYPOINT = "data.codeyourcompliance.os_package_baseline"


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"timestamp must be UTC and end with Z: {value!r}")
    return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_instance(instance: dict[str, Any], schema_path: Path) -> list[str]:
    validator = Draft202012Validator(load_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    return [f"{'.'.join(str(p) for p in error.absolute_path) or '$'}: {error.message}" for error in errors]


def opa_version(command: str) -> str | None:
    if shutil.which(command) is None:
        return None
    proc = subprocess.run([command, "version"], text=True, capture_output=True, check=False)
    return proc.stdout.strip().splitlines()[0] if proc.returncode == 0 and proc.stdout.strip() else None


def derive_facts(evidence: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    observed = {item["name"]: item["version"] for item in evidence["observations"]["packages"]}
    required = {item["name"]: item["version"] for item in context["required_packages"]}
    missing = [{"name": name, "required_version": version} for name, version in sorted(required.items()) if name not in observed]
    mismatches = [
        {"name": name, "observed_version": observed[name], "required_version": version}
        for name, version in sorted(required.items())
        if name in observed and observed[name] != version
    ]
    unexpected = [{"name": name, "version": version} for name, version in sorted(observed.items()) if name not in required]
    return {"missing_packages": missing, "version_mismatches": mismatches, "unexpected_packages": unexpected}


def evaluate_builtin(facts: dict[str, Any], mode: str) -> tuple[str, list[dict[str, str]]]:
    violations: list[dict[str, str]] = []
    for pkg in facts["missing_packages"]:
        violations.append({"code": "MISSING_REQUIRED_PACKAGE", "message": f"required package missing: {pkg['name']}"})
    for item in facts["version_mismatches"]:
        violations.append({"code": "PACKAGE_VERSION_MISMATCH", "message": f"package {item['name']} is {item['observed_version']}; required {item['required_version']}"})
    if mode == "fail":
        for pkg in facts["unexpected_packages"]:
            violations.append({"code": "UNEXPECTED_PACKAGE", "message": f"unexpected package observed: {pkg['name']} {pkg['version']}"})
    return ("pass" if not violations else "fail"), violations


def evaluate_opa(policy: Path, opa_input: dict[str, Any], command: str) -> tuple[str, list[dict[str, Any]]]:
    if shutil.which(command) is None:
        raise RuntimeError(f"OPA executable not found: {command}")
    proc = subprocess.run(
        [command, "eval", "--format=json", "--data", str(policy), "--stdin-input", OPA_ENTRYPOINT],
        input=json.dumps(opa_input), text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"OPA failed: {proc.stderr.strip()}")
    value = json.loads(proc.stdout)["result"][0]["expressions"][0]["value"]
    return ("pass" if value.get("allow", False) else "fail"), value.get("violations", [])


def replay(evidence_path: Path, digest_path: Path, context_path: Path,
           evidence_schema_path: Path, context_schema_path: Path,
           policy_path: Path, policy_engine: str, opa_command: str) -> dict[str, Any]:
    evidence = load_json(evidence_path)
    context = load_json(context_path)
    result: dict[str, Any] = {
        "assessment_schema_version": "0.1.0",
        "implementation": {"name": "codeyourcompliance.os_package_baseline", "version": IMPLEMENTATION_VERSION,
                           "python_version": platform.python_version(),
                           "opa_version": opa_version(opa_command) if policy_engine == "opa" else None},
        "artifacts": {
            "evidence": {"path": str(evidence_path), "sha256": file_sha256(evidence_path)},
            "evidence_schema": {"path": str(evidence_schema_path), "sha256": file_sha256(evidence_schema_path)},
            "evaluation_context": {"path": str(context_path), "sha256": file_sha256(context_path)},
            "context_schema": {"path": str(context_schema_path), "sha256": file_sha256(context_schema_path)},
            "policy": {"path": str(policy_path), "sha256": file_sha256(policy_path), "entrypoint": OPA_ENTRYPOINT}},
        "evidence_id": evidence.get("evidence_id"), "evidence_status": "unknown", "context_status": "unknown",
        "control_status": "unknown", "decision_engine": policy_engine, "decision_executed": False,
        "policy_artifact": {"executed": False, "engine": policy_engine}, "derived_facts": {}, "violations": [], "gate_trace": []}

    errors = validate_instance(evidence, evidence_schema_path)
    if errors:
        result["evidence_status"] = "invalid_evidence"
        result["gate_trace"].append({"gate": "evidence_schema", "status": "failed", "errors": errors})
        return result
    result["gate_trace"].append({"gate": "evidence_schema", "status": "passed"})

    errors = validate_instance(context, context_schema_path)
    if errors:
        result["context_status"] = "invalid_context"
        result["gate_trace"].append({"gate": "context_schema", "status": "failed", "errors": errors})
        return result
    result["context_status"] = "valid"
    result["gate_trace"].append({"gate": "context_schema", "status": "passed"})

    expected = digest_path.read_text(encoding="utf-8").strip().lower()
    actual = file_sha256(evidence_path)
    if expected != actual:
        result["evidence_status"] = "invalid_evidence"
        result["gate_trace"].append({"gate": "integrity", "status": "failed", "expected_sha256": expected, "actual_sha256": actual})
        return result
    result["gate_trace"].append({"gate": "integrity", "status": "passed", "sha256": actual})

    collected = parse_utc(evidence["timestamps"]["collected_at_utc"])
    evaluated = parse_utc(context["evaluated_at_utc"])
    age_hours = (evaluated - collected).total_seconds() / 3600
    result["derived_facts"]["evidence_age_hours"] = age_hours
    if age_hours < 0 or age_hours > float(context["max_evidence_age_hours"]):
        result["evidence_status"] = "stale_evidence"
        result["gate_trace"].append({"gate": "freshness", "status": "failed", "evidence_age_hours": age_hours})
        return result
    result["gate_trace"].append({"gate": "freshness", "status": "passed", "evidence_age_hours": age_hours})

    facts = derive_facts(evidence, context)
    result["derived_facts"].update(facts)
    result["evidence_status"] = "valid"
    opa_input = {"evidence": evidence, "context": context, "derived_facts": result["derived_facts"]}
    if policy_engine == "opa":
        status, violations = evaluate_opa(policy_path, opa_input, opa_command)
        result["policy_artifact"]["executed"] = True
    else:
        status, violations = evaluate_builtin(facts, context["unexpected_package_mode"])
    result["decision_executed"] = True
    result["control_status"] = status
    result["violations"] = violations
    result["gate_trace"].append({"gate": "decision", "status": "executed", "engine": policy_engine,
                                 "policy_artifact_executed": result["policy_artifact"]["executed"]})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay an OS package baseline evidence package")
    for name in ("evidence", "digest", "context", "evidence-schema", "context-schema", "policy", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--policy-engine", choices=("builtin", "opa"), default="builtin")
    parser.add_argument("--opa-command", default="opa")
    args = parser.parse_args()
    try:
        result = replay(args.evidence, args.digest, args.context, args.evidence_schema, args.context_schema,
                        args.policy, args.policy_engine, args.opa_command)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"replay failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
