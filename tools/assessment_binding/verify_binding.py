#!/usr/bin/env python3
"""Bounded synthetic assessment-run-to-baseline binding comparison.

Does not authenticate the caller, baseline, binding record, or historical run.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PROFILE = "tls-replay-v0.1"
BASELINE_TYPE = "synthetic_tls_recorded_assessment_v0.1"
BINDING_TYPE = "synthetic_tls_assessment_run_binding_v0.1"
RUN_REF = re.compile(r"synthetic-tls-run-[0-9]{3}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_FILE_BYTES = 1024 * 1024
ARTIFACT_ROLES = (
    "evidence", "evidence_digest", "evidence_schema", "evaluation_context",
    "context_schema", "policy", "replay_implementation", "runtime_requirements",
)


class InputError(Exception):
    """Indicates an unavailable or invalid synthetic input."""

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def load_object(path, kind):
    try:
        source = Path(path)
        with source.open("rb") as handle:
            payload = handle.read(MAX_FILE_BYTES + 1)
    except (OSError, ValueError, TypeError) as exc:
        raise InputError(kind + "_unavailable") from exc
    if len(payload) > MAX_FILE_BYTES:
        raise InputError(kind + "_too_large")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def no_non_json_constants(value):
        raise ValueError("invalid JSON constant")

    try:
        obj = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=unique_pairs,
            parse_constant=no_non_json_constants,
        )
    except (ValueError, UnicodeError) as exc:
        raise InputError(kind + "_invalid_json") from exc
    if not isinstance(obj, dict):
        raise InputError(kind + "_invalid_json")
    return obj, hashlib.sha256(payload).hexdigest()


def is_digest(value):
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def is_run_ref(value):
    return isinstance(value, str) and RUN_REF.fullmatch(value) is not None


def valid_artifacts(value):
    return (
        isinstance(value, dict)
        and set(value) == set(ARTIFACT_ROLES)
        and all(is_digest(value[role]) for role in ARTIFACT_ROLES)
    )


def validate_baseline(value):
    if (
        value.get("record_type") != BASELINE_TYPE
        or value.get("profile") != PROFILE
        or value.get("authority") != "unattested_synthetic_fixture"
        or not is_run_ref(value.get("assessment_run_ref"))
        or not valid_artifacts(value.get("artifact_sha256"))
        or not isinstance(value.get("recorded"), dict)
        or value["recorded"].get("decision_engine") != "builtin"
        or value["recorded"].get("decision_executed") is not True
        or value["recorded"].get("control_status") not in ("pass", "fail")
    ):
        raise InputError("unsupported_synthetic_baseline")


def validate_binding(value):
    if (
        value.get("record_type") != BINDING_TYPE
        or value.get("profile") != PROFILE
        or value.get("reference_origin") != "co_packaged_unattested"
        or not is_run_ref(value.get("assessment_run_ref"))
        or not is_digest(value.get("baseline_sha256"))
        or not valid_artifacts(value.get("artifact_sha256"))
    ):
        raise InputError("unsupported_synthetic_binding")


def verify(baseline_path, binding_path, requested_run_ref):
    """Return deterministic (receipt, exit_code); reads inputs, never makes a decision."""
    receipt = {
        "receipt_version": "0.1.0",
        "profile": PROFILE,
        "verification_status": "blocked",
        "requested_assessment_run_ref": requested_run_ref if is_run_ref(requested_run_ref) else None,
        "baseline_assessment_run_ref": None,
        "binding_assessment_run_ref": None,
        "baseline_sha256": None,
        "reference_baseline_sha256": None,
        "binding_record_sha256": None,
        "baseline_digest_match": None,
        "artifact_bindings_match": None,
        "reason_codes": [],
        "binding_record_authentication": "not_assessed",
        "binding_record_independence": "not_assessed",
        "assessment_origin_authentication": "not_assessed",
        "historical_replay_verified": False,
        "decision_executed": False,
        "control_status": "unknown",
    }
    try:
        if not is_run_ref(requested_run_ref):
            raise InputError("invalid_requested_assessment_run_ref")
        baseline, baseline_sha = load_object(baseline_path, "baseline")
        validate_baseline(baseline)
        receipt["baseline_sha256"] = baseline_sha
        receipt["baseline_assessment_run_ref"] = baseline["assessment_run_ref"]

        binding, binding_sha = load_object(binding_path, "binding")
        validate_binding(binding)
        receipt["binding_record_sha256"] = binding_sha
        receipt["binding_assessment_run_ref"] = binding["assessment_run_ref"]
        receipt["reference_baseline_sha256"] = binding["baseline_sha256"]

        digest_match = baseline_sha == binding["baseline_sha256"]
        role_match = baseline["artifact_sha256"] == binding["artifact_sha256"]
        receipt["baseline_digest_match"] = digest_match
        receipt["artifact_bindings_match"] = role_match
        problems = []
        if not digest_match:
            problems.append("baseline_digest_differs_from_binding")
        if baseline["assessment_run_ref"] != binding["assessment_run_ref"]:
            problems.append("baseline_run_ref_differs_from_binding")
        if not role_match:
            problems.append("artifact_references_differ")
        if problems:
            receipt["verification_status"] = "binding_mismatch"
            receipt["reason_codes"] = problems
            return receipt, 1

        if requested_run_ref != binding["assessment_run_ref"]:
            receipt["verification_status"] = "requested_run_mismatch"
            receipt["reason_codes"] = ["requested_run_ref_differs_from_binding"]
            return receipt, 1

        receipt["verification_status"] = "binding_consistent"
        return receipt, 0
    except InputError as exc:
        receipt["reason_codes"] = [exc.reason]
        return receipt, 2


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check synthetic TLS run identity against an unattested baseline binding record."
    )
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--requested-run-ref", required=True)
    args = parser.parse_args(argv)
    receipt, code = verify(args.baseline, args.binding, args.requested_run_ref)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
