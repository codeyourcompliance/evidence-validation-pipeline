# Current Implementation Status

This document states what the `evidence-validation-pipeline` repository currently implements, what it models, and what remains out of scope.

The purpose is to avoid treating architecture language as finished implementation.

This repository is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, or certification advice.

## Implemented

The repository currently includes:

| Area | Current artifact |
| --- | --- |
| Read-only baseline collection | `ansible/collect_system_info.yml` |
| System baseline evidence example | `examples/sample_system_baseline.json` |
| TLS lifecycle evidence example | `examples/sample_evidence.json` |
| Minimum replay-aware evidence object | `examples/minimal_evidence_object.json` |
| Invalid evidence result | `examples/invalid_evidence_result.json` |
| Stale evidence example | `examples/stale_evidence.json` |
| Evidence freshness admissibility policy demo | `policies/demo/evidence_freshness.rego` |
| Evidence admissibility gate contract | `docs/evidence-admissibility-gate.md` |
| Replayable TLS control reference package | `examples/replayable-tls-control/` |
| Evidence and evaluation-context schema gates for the TLS reference package | `examples/replayable-tls-control/schema/` |
| Computed SHA256 artifact provenance and evidence integrity gate for TLS replay | `examples/replayable-tls-control/replay.py` |
| Deterministic TLS replay runner with built-in and OPA decision paths | `examples/replayable-tls-control/replay.py` |
| Collector provenance contract | `docs/collector-provenance-contract.md` |
| Synthetic collector provenance comparison | `examples/collector-provenance/` |
| Minimum workflow-proof evidence object | `examples/minimal_workflow_proof_object.json` |
| Invalid workflow-proof evidence result | `examples/invalid_workflow_proof_missing_review_owner.json` |
| Sample audit narrative | `examples/sample_report.md` |
| Evidence replay checklist | `docs/evidence-replay-checklist.md` |
| Screenshot evidence classification | `docs/screenshot-evidence-gap.md` |
| Evidence-before-reporting boundary | `docs/week-3-evidence-before-reporting.md` |
| Workflow-proof boundary | `docs/workflow-proof-boundary.md` |

The replayable TLS package is a bounded reference implementation. Its capabilities should not be read as repo-wide enforcement across every example.

The collector provenance example is synthetic. It models provenance semantics; it does not implement cryptographic collector attestation or automated collector equivalence testing.

## Modeled

The repository models these boundaries:

- observation vs remediation
- read-only collection vs collection provenance
- target-state change vs collector change
- checklist row vs evidence requirement
- screenshot vs proof object
- evidence processing vs audit conclusion
- delivery evidence vs workflow evidence
- tool approval vs workflow proof
- evidence integrity vs evidence freshness
- evidence admissibility evaluation vs control decision evaluation
- stale evidence vs failed control
- invalid evidence vs failed control

These boundaries are part of the public technical model.

They are not complete product features.

## Not Yet Implemented

The repository does not yet implement:

- signed manifests
- trusted timestamping
- immutable evidence storage
- cryptographic binding of collector implementation digests to evidence objects
- automated collector-version equivalence testing
- repo-wide schema enforcement across all evidence examples
- a generic replay runner across evidence types
- a full OPA/Rego policy pack
- workflow-level policy evaluation
- end-to-end evidence package generation

The workflow-proof examples are synthetic evidence objects.

They are not a full workflow-proof engine.

The freshness policy is a narrow evidence-admissibility demo policy.

It is not a downstream control policy or a complete evidence integrity policy pack.

The replayable TLS package implements schema, integrity, freshness, replay, and decision gates for one bounded TLS scenario. It is not a generic compliance evaluation engine.

## Design Rule

Do not evaluate a control claim from inadmissible evidence.

If evidence schema validation or integrity verification fails, the control decision should not run.

If evidence freshness has expired, classify the evidence as stale and block the downstream control decision.

If evaluation context is invalid, block the control decision rather than manufacturing a control failure.

If collector identity, version, method, parser, or source path changes, preserve that difference before classifying an observation difference as target-state drift.

If the evidence source is unclear, classify the artifact before using it.

If the artifact is only a claim, treat it as a claim.

The state boundary is:

```text
decision_executed = false
=> control_status = unknown
```

The provenance boundary is:

```text
observation difference
+ collector difference
=> target drift not yet established
```

## Boundary Statement

This repository is an evidence engineering demonstration.

It does not claim MAS TRM compliance.

It does not replace formal control ownership, risk assessment, audit review, or regulatory interpretation.

The audit boundary starts before the report.
