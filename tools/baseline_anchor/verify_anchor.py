#!/usr/bin/env python3
"""Read-only, bounded SHA256 comparison for an unattested synthetic TLS baseline."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PROFILE = "tls-replay-v0.1"
BASELINE_TYPE = "synthetic_tls_recorded_assessment_v0.1"
SELF_REFERENCE_TYPE = "synthetic_self_supplied_baseline_digest_v0.1"
MAX_FILE_BYTES = 1024 * 1024
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class InputError(Exception):
    """An input cannot be safely compared."""

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def read_limited(path, unavailable, too_large):
    try:
        file_path = Path(path)
        if not file_path.is_file():
            raise InputError(unavailable)
        with file_path.open("rb") as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    except (OSError, ValueError) as exc:
        raise InputError(unavailable) from exc
    if len(payload) > MAX_FILE_BYTES:
        raise InputError(too_large)
    return payload


def parse_object(payload, reason):
    def unique_pairs(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON key")
            obj[key] = value
        return obj

    def reject_constant(value):
        raise ValueError("non-JSON numeric constant")

    try:
        result = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=unique_pairs,
            parse_constant=reject_constant,
        )
    except (UnicodeError, ValueError) as exc:
        raise InputError(reason) from exc
    if not isinstance(result, dict):
        raise InputError(reason)
    return result


def validate_baseline(payload):
    baseline = parse_object(payload, "invalid_baseline_json")
    if (
        baseline.get("record_type") != BASELINE_TYPE
        or baseline.get("profile") != PROFILE
        or baseline.get("authority") != "unattested_synthetic_fixture"
        or not isinstance(baseline.get("recorded"), dict)
        or not isinstance(baseline.get("artifact_sha256"), dict)
    ):
        raise InputError("unsupported_baseline_profile")


def validate_self_reference(payload):
    reference = parse_object(payload, "invalid_self_reference_json")
    if (
        reference.get("record_type") != SELF_REFERENCE_TYPE
        or reference.get("profile") != PROFILE
        or reference.get("reference_origin") != "co_packaged_unattested"
    ):
        raise InputError("unsupported_self_reference")
    expected = reference.get("baseline_sha256")
    if not isinstance(expected, str) or SHA256_RE.fullmatch(expected) is None:
        raise InputError("invalid_reference_sha256")
    return expected


def verify(baseline_path, self_reference_path=None, expected_sha256=None):
    """Return (receipt, exit_code); never modify evidence or execute a decision."""
    mode = (
        "self_supplied_sidecar"
        if self_reference_path is not None
        else "operator_pinned_digest"
    )
    receipt = {
        "receipt_version": "0.1.0",
        "profile": PROFILE,
        "reference_mode": mode,
        "verification_status": "blocked",
        "baseline_sha256": None,
        "reference_sha256": None,
        "digest_match": None,
        "reason_codes": [],
        "reference_independence": "not_assessed",
        "reference_authentication": "not_assessed",
        "baseline_origin_authentication": "not_assessed",
        "historical_replay_verified": False,
        "decision_executed": False,
        "control_status": "unknown",
    }
    try:
        if (self_reference_path is None) == (expected_sha256 is None):
            raise InputError("exactly_one_reference_required")
        if expected_sha256 is not None and (
            not isinstance(expected_sha256, str)
            or SHA256_RE.fullmatch(expected_sha256) is None
        ):
            raise InputError("invalid_reference_sha256")
        baseline_bytes = read_limited(
            baseline_path, "baseline_unavailable", "baseline_too_large"
        )
        validate_baseline(baseline_bytes)
        observed = hashlib.sha256(baseline_bytes).hexdigest()
        receipt["baseline_sha256"] = observed
        if self_reference_path is not None:
            reference_bytes = read_limited(
                self_reference_path,
                "self_reference_unavailable",
                "self_reference_too_large",
            )
            expected = validate_self_reference(reference_bytes)
        else:
            expected = expected_sha256
        receipt["reference_sha256"] = expected
        receipt["digest_match"] = observed == expected
        if observed != expected:
            receipt["verification_status"] = "reference_mismatch"
            receipt["reason_codes"] = ["baseline_digest_differs_from_reference"]
            return receipt, 1
        receipt["verification_status"] = (
            "self_consistent" if self_reference_path is not None else "pinned_match"
        )
        return receipt, 0
    except InputError as exc:
        receipt["reason_codes"] = [exc.reason]
        return receipt, 2


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Compare an unattested synthetic TLS baseline against a co-packaged "
            "self-reference or a caller-pinned SHA256. No authentication is claimed."
        )
    )
    parser.add_argument("--baseline", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-reference", help="Unattested mutable sidecar digest JSON")
    group.add_argument(
        "--expected-sha256",
        help="Digest supplied separately by caller; its source is NOT authenticated",
    )
    args = parser.parse_args(argv)
    receipt, exit_code = verify(
        args.baseline, args.self_reference, args.expected_sha256
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
