"""Offline, read-only byte/dependency checker for one bounded TLS replay profile.

This tool does not execute replay, authenticate origins, or establish control status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

PROFILE = "tls-replay-v0.1"
REQUIRED_ROLES = (
    "evidence",
    "evidence_digest",
    "evidence_schema",
    "evaluation_context",
    "context_schema",
    "policy",
    "replay_implementation",
    "runtime_requirements",
)
HEX64 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
MAX_MANIFEST_BYTES = 256 * 1024
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


class DuplicateKeyError(ValueError):
    pass


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def issue(code: str, *, role: str | None = None, path: str | None = None) -> dict[str, str]:
    item = {"code": code}
    if role is not None:
        item["role"] = role
    if path is not None:
        item["path"] = path
    return item


def result_template() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "profile": None,
        "closure_status": "blocked",
        "checks": [],
        "issues": [],
        "replay_executed": False,
        "decision_executed": False,
        "control_status": "unknown",
        "manifest_authentication_status": "not_assessed",
        "source_authority_status": "not_assessed",
        "runtime_availability_status": "not_assessed",
    }


def valid_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    if value.startswith("/") or any(ord(char) < 32 for char in value):
        return False
    parts = value.split("/")
    if any(part in ("", ".", "..") or part.endswith((".", " ")) for part in parts):
        return False
    if any(part.split(".", 1)[0].upper() in WINDOWS_RESERVED for part in parts):
        return False
    return True


def validate_structure(data: Any) -> list[dict[str, str]]:
    problems: list[dict[str, str]] = []
    if not isinstance(data, dict) or set(data) != {"manifest_version", "profile", "artifacts"}:
        return [issue("invalid_manifest_shape")]
    if data["manifest_version"] != "0.1.0" or data["profile"] != PROFILE:
        problems.append(issue("unsupported_profile_or_version"))
    artifacts = data["artifacts"]
    if not isinstance(artifacts, list):
        return problems + [issue("invalid_artifacts")]
    roles: set[str] = set()
    paths: set[str] = set()
    for entry in artifacts:
        if not isinstance(entry, dict) or set(entry) != {"role", "path", "sha256"}:
            problems.append(issue("invalid_artifact_entry"))
            continue
        role, path, digest = entry["role"], entry["path"], entry["sha256"]
        if not isinstance(role, str) or role not in REQUIRED_ROLES:
            problems.append(issue("unknown_role"))
        elif role in roles:
            problems.append(issue("duplicate_role", role=role))
        else:
            roles.add(role)
        if not valid_relative_path(path):
            problems.append(issue("invalid_path", role=role if isinstance(role, str) else None))
        elif path.casefold() in paths:
            problems.append(issue("duplicate_path", role=role if isinstance(role, str) else None, path=path))
        else:
            paths.add(path.casefold())
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            problems.append(issue("invalid_sha256", role=role if isinstance(role, str) else None))
    for role in REQUIRED_ROLES:
        if role not in roles:
            problems.append(issue("missing_required_role", role=role))
    return problems


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(manifest_path: Path) -> dict[str, Any]:
    result = result_template()
    try:
        if manifest_path.is_symlink():
            result["issues"].append(issue("symlink_manifest_disallowed"))
            return result
        if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
            result["issues"].append(issue("manifest_too_large"))
            return result
        data = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    except (OSError, ValueError, UnicodeError):
        result["issues"].append(issue("manifest_read_or_parse_error"))
        return result

    if isinstance(data, dict) and isinstance(data.get("profile"), str):
        result["profile"] = data["profile"]
    problems = validate_structure(data)
    if problems:
        result["issues"] = problems
        return result

    root = manifest_path.parent.resolve()
    checked: dict[str, tuple[Path, str]] = {}
    for entry in data["artifacts"]:
        role, relative, expected = entry["role"], entry["path"], entry["sha256"]
        target = root.joinpath(*relative.split("/"))
        check: dict[str, str] = {"role": role, "path": relative}
        result["checks"].append(check)
        # Refuse symlinks at every level, including the final file.
        ancestor = root
        unsafe_link = False
        for segment in relative.split("/"):
            ancestor = ancestor / segment
            if ancestor.is_symlink():
                unsafe_link = True
                break
        if unsafe_link:
            check["status"] = "symlink_disallowed"
            result["issues"].append(issue("symlink_disallowed", role=role, path=relative))
            continue
        if not target.is_file():
            check["status"] = "missing_or_not_file"
            result["issues"].append(issue("missing_or_not_file", role=role, path=relative))
            continue
        try:
            actual = hash_file(target)
        except OSError:
            check["status"] = "read_error"
            result["issues"].append(issue("read_error", role=role, path=relative))
            continue
        check["status"] = "sha256_match" if actual == expected else "sha256_mismatch"
        check["actual_sha256"] = actual
        if actual != expected:
            result["issues"].append(issue("sha256_mismatch", role=role, path=relative))
        else:
            checked[role] = (target, actual)

    # The replay runner also reads a separate expected digest file.
    # Both files being listed in the manifest is not enough: their values must agree.
    if "evidence" in checked and "evidence_digest" in checked:
        target, _ = checked["evidence_digest"]
        try:
            digest_text = target.read_text(encoding="ascii").strip()
        except (OSError, UnicodeError):
            result["issues"].append(issue("invalid_evidence_digest_file", role="evidence_digest"))
        else:
            if HEX64.fullmatch(digest_text) is None or digest_text != checked["evidence"][1]:
                result["issues"].append(issue("evidence_digest_binding_mismatch", role="evidence_digest"))

    if not result["issues"]:
        result["closure_status"] = "satisfied"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline TLS replay package dependency and byte checker")
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    report = validate(args.manifest)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["closure_status"] == "satisfied" else 1


if __name__ == "__main__":
    sys.exit(main())
