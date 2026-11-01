# Evidence Package Closure Contract

An intact evidence file is not necessarily a replayable evidence package.

A reviewer may have the original `evidence.json` and a matching digest but no longer have the evaluation context or policy artifact used for the recorded assessment.

This contract defines a bounded CodeYourCompliance engineering boundary:

```text
individual artifact digest matches
!=
required replay inputs are available
```

## Scope

This contract accompanies an offline, standard-library Python validator for the existing `examples/replayable-tls-control/` reference package.

It is a MAS TRM-inspired engineering interpretation. It is not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.

The validator tests **byte availability and digest correspondence for one predeclared TLS replay profile**. It does not test the correctness of the policy, the collector, the source state, or the assessment.

## Failure Mode

An assessment result records `PASS`.

Three months later, the original evidence JSON still verifies against an expected SHA256 digest. However, the evaluation-context file is missing, or the only policy file now available is a different version.

A reviewer cannot reconstruct the original evaluation from the surviving evidence file alone.

Do not convert a failed replay preflight into a retrospective control `FAIL`. Equally, the historical `PASS` is not independent proof of successful replay.

```text
historical_result = recorded_pass
closure_status = blocked
replay_executed = false
control_status = unknown
```

The historical result is a separate record. The `unknown` state here describes the **new, unexecuted evaluation**, not an automatic rewrite of the historical result.

## Fixed TLS Profile v0.1

The checker uses the fixed profile `tls-replay-v0.1`. Required roles and relative paths are specified in validator code, not inferred solely from the manifest.

| Required role | Expected relative path |
| --- | --- |
| evidence | `input/evidence.json` |
| evidence_digest | `input/evidence.sha256` |
| evidence_schema | `schema/evidence.schema.json` |
| evaluation_context | `input/evaluation-context.json` |
| context_schema | `schema/context.schema.json` |
| policy | `policy/tls_certificate.rego` |
| replay_implementation | `replay.py` |
| runtime_requirements | `requirements.txt` |

The manifest is stored at `examples/replayable-tls-control/closure-manifest.json`.

Each entry declares exactly `role`, `path`, and a lowercase 64-character hexadecimal `sha256` value.

The validator rejects unknown or duplicate roles, missing required roles, duplicate paths, unexpected role-to-path mappings, malformed digests, and unsupported manifest versions or profiles. It does not accept arbitrary additional roles for v0.1.

The manifest may change in a later profile, but such a change is a profile revision, not silent compatibility.

## Checks Performed

The read-only preflight:

1. Parses a bounded-size JSON manifest and rejects duplicate JSON keys.
2. Checks required roles against the hardcoded profile and expected paths.
3. Rejects absolute paths, traversal components, Windows drive paths, backslashes, reserved device names, and case-insensitive duplicate paths.
4. Rejects symlinks along referenced file paths.
5. Checks that every required path exists as a regular file.
6. Streams each file into SHA256 and compares the computed digest with the manifest.
7. Separately checks that the `input/evidence.sha256` file contains the computed digest of `input/evidence.json`.

Any failure blocks closure. It cannot be bypassed by removing the corresponding role from the manifest.

The checker does not change evidence files, produce a repaired package, or use network access.

## Result Semantics

The JSON output exposes:

```json
{
  "closure_status": "satisfied",
  "issues": [],
  "replay_executed": false,
  "decision_executed": false,
  "control_status": "unknown",
  "manifest_authentication_status": "not_assessed",
  "source_authority_status": "not_assessed",
  "runtime_availability_status": "not_assessed"
}
```

This is an illustrative projection of the successful result. The actual output also includes the selected profile, schema version, and per-artifact checks.

- `satisfied` means that the current files satisfy the fixed TLS profile's role, path, and byte checks against the supplied manifest. It does **not** mean replay succeeded.
- `blocked` means at least one structural, file, digest, or binding requirement failed. The `issues` list gives machine-readable reasons.
- Exit status `0` corresponds to `satisfied`; `1` corresponds to `blocked`.

The validator never emits a control `PASS` or `FAIL`.

## Checkout Byte Fidelity

The v0.1 manifest records SHA256 of the exact LF bytes committed for the eight TLS replay inputs. This is a byte-level identity check, not a semantic JSON or text comparison.

On a Windows clone using `core.autocrlf=true`, Git may have converted these files to CRLF at checkout. Such files may be considered clean by Git after line-ending normalization but still produce different raw SHA256 values. Closure must remain blocked rather than accepting both byte representations implicitly.

The repository's [root `.gitattributes`](../.gitattributes) now pins `eol=lf` for the manifest and eight referenced files. Existing clones may need to rewrite those tracked worktree files after updating; see the [Windows repair instructions](../tools/evidence_package_closure/README.md#windows-line-ending-repair-after-upgrading-an-existing-clone).

The test suite includes a real checked-in TLS fixture check so that checkout conversion errors do not remain hidden behind synthetic temporary-file tests.

## What the Manifest Does Not Prove

A manifest containing hashes is not automatically an authenticated baseline.

If an attacker can rewrite both the package files and the manifest, a new internally consistent set can satisfy the checks. No signed manifest, trusted digest registry, or immutable store is implemented here.

A reference profile can specify the roles this checker expects. It cannot, without additional requirements and evidence, prove that every runtime or external dependency needed for historical replay has been captured.

In particular:

- Hashing `requirements.txt` does not prove that the required Python libraries or compatible interpreter are installed or preserved.
- Hashing `replay.py` does not prove that its execution environment and toolchain match the historical environment.
- Hashing a Rego policy does not show that the built-in decision path actually executed that policy.
- Hashing schema files does not execute schema validation or establish the schemas' correctness.
- This checker does not invoke OPA, install dependencies, run the replay implementation, validate source authority, or authenticate the manifest.
- Local file checking is not a concurrency-safe custody or immutable-storage mechanism. Files might change after preflight.

Those are separate implementation and assurance layers.

## Relationship to Existing Artifacts

The existing [Replayable TLS Control](../examples/replayable-tls-control/) provides a bounded assessment runner with schema, integrity, freshness, and decision stages.

This closure validator is a **preflight**, not a replacement for those stages.

See also:

- [Evidence Replay Checklist](evidence-replay-checklist.md)
- [Policy Evaluation Provenance Contract](policy-evaluation-provenance-contract.md)
- [Evidence Custody and Authenticity Contract](evidence-custody-authenticity-contract.md)

## Verification and Limits

The validator and its tests are located in `tools/evidence_package_closure/`.

The tests use synthetic temporary files and Python's standard library. They cover satisfied closure, missing roles, missing files, digest mismatch, cross-file digest binding mismatch, malformed manifests, traversal, Windows path rules, symlink rejection, exact role path mapping, and deterministic read-only behavior.

No Windows-native runtime execution, installed OPA dependency, or end-to-end control assessment is implied by these tests.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.

## Final Boundary

Package closure is a check on declared local replay inputs.

A closure result is not a policy decision.

A matching manifest is not authenticated origin.
