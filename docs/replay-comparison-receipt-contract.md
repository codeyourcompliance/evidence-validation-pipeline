# Replay Comparison Receipt Contract v0.1

A second `PASS` is not, by itself, a historical replay result.

## Failure mode

An analyst opens a stored assessment and sees `PASS`. A replay run against a newer context or different policy also reports `PASS`. The tool declares replay successful because it compared only the final result. That conclusion is unsupported. The inputs and evaluation path may be different.

The same risk exists when the package is complete and all current SHA256 values match the current manifest. Completeness against today's manifest is not proof that those were the original assessment inputs.

## Engineering boundary

This CodeYourCompliance example uses a MAS TRM-inspired engineering interpretation. MAS TRM does not prescribe this comparator or its receipt schema. This is not legal, regulatory, audit, certification, procurement, or compliance advice.

The program runs the existing synthetic TLS runner. The recorded reference is explicitly an **unattested synthetic fixture**, not a capture from a trusted historical system. A `matched` result means only that the current execution agrees with the asserted fixture on the defined fields and byte references.

## Comparison sequence

1. Load and validate the recorded fixture shape. Reject duplicate JSON keys and unsupported profile/engine declarations.
2. Run the existing TLS package closure validator against the manifest. If blocked, do not run a decision.
3. Match all eight artifact SHA256 bindings in the recorded fixture to the manifest's current pinned role/path entries. Compare selected engine before execution.
4. Launch the existing `replay.py` using those pinned package paths and a temporary output. This is **execution**, not a modeled result.
5. Verify the closure boundary again, compare replay output artifact hashes, engine path, policy-artifact execution flag, implementation identity/version, and selected stable decision fields.
6. Produce a comparison receipt with explicit status and reasons. The receipt is outside the evidence package and is never treated as a control assessment.

### Compared decision fields

The v0.1 stable comparison includes `evidence_id`, `evidence_status`, `context_status`, `control_status`, `violations`, and `derived_facts`. The engine/provenance comparison separately includes `decision_engine`, `policy_artifact.executed`, `policy_artifact.engine`, and replay implementation name/version.

Python and OPA runtime versions are not asserted equivalent. Gate trace equivalence, output timestamps, environment variables, transitive dependencies, and policy semantics are not independently verified.

## Status and decision boundaries

| Status | Meaning |
| --- | --- |
| `matched` | Current run agrees with the **provided** synthetic recorded fixture on the checked references and fields |
| `input_mismatch` | Recorded vs current artifact references, engine path, implementation provenance, or actual runner input hashes do not agree |
| `decision_mismatch` | A decision was executed, but the compared result differs |
| `blocked` | Preflight, recorded fixture, execution, or replay result validation failed |

The receipt always records:

```text
baseline_authentication = not_assessed
manifest_authentication = not_assessed
runtime_equivalence = not_assessed
historical_replay_verified = false
```

In particular:

```text
comparison_status = matched
!=
historical assessment independently authenticated
```

A package closure failure is not a control failure. A comparison mismatch is not, on its own, evidence of target drift. A built-in decision is not evidence that the Rego artifact was executed.

The baseline can be replaced together with the manifest and files. Hashing an untrusted baseline does not create a trusted historical reference. Authenticate/anchor the baseline and preserve its custody independently before making stronger claims.

The comparator does not collect evidence or remediate systems. It produces a current-run comparison, not an audit approval or certification decision.

## Implementation scope

- Fixed `tls-replay-v0.1` roles, paths, and one synthetic TLS scenario.
- Python comparator with standard-library dependencies. The existing TLS runner retains its `jsonschema` dependency; OPA is optional and not part of the included `builtin` baseline.
- Offline local execution, read-only source evidence, temporary intermediate replay output.
- Tests use synthetic temporary packages and a fake subprocess runner to exercise control flow. Only a separate integration run against the checked-in TLS package establishes that the existing runner executed.
- No generic replay engine, signed receipt, authenticated historical baseline, immutable audit log, trusted clock, OPA parity certification, historical environment equivalence, or independent origin attestation.

## Origin and attribution

This material originates from **CodeYourCompliance**.

Website: https://www.codeyourcompliance.com

GitHub: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.
